from rest_framework import serializers
from rest_framework.utils import model_meta
from copy import deepcopy
import traceback
from enum import Enum
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail
from django.core.exceptions import ValidationError as DjangoValidationError
from collections.abc import Mapping
from rest_framework.fields import SkipField
from rest_framework.settings import api_settings


class BaseWritableNestedSerializer(serializers.ModelSerializer):
    """
    Serializer class which can be extended to support Creation/Updation of
    nested serializer's data.

    For OneToOneField & ForeignKey fields:
        Nested serializer will not have many=True.
        Input payload for such fields will be like below
        Eg. {
                field: { #json
                    "key": "value"
                }
            }
        If there is FK or O2O data associated already with the instance, this class will
        update that data with the provided json values. If there is no data associated
        with FK or O2O field, this class will create data and assign it to field.

        NOTE: primary key field is not required for creation or updation of FK or O2O field.

        If you want to replace/remove data associated with FK or O2O field, pass
        following json
        Eg. {
                field: { #json
                    "id": value,
                    "link": true/false
                }
            }
        If 'link' value is True, this class will replace field value with the
        object associated with 'id'. If link is false, this class will set FK or O2O
        field value to None. 'id' here is the name of your model's primary key. If
        the primary key of model is named something other than id, use that name

    For ManyToMany fields:
        Nested serializer will have many=True.
        Input payload for such fields will be like below
        Eg. {
                field: [ #list
                    { #1
                        "id": value
                        "key": "value
                    },
                    { #2
                        "key": "value
                    },
                    { #3
                        "id": value,
                        "link": true/false
                    }

                ]
            }
        Three types of json can be passed inside list for M2M field as shown above with
        #1, #2 & #3.

        #1: If 'id' is passed, this class will update the object corresponding to id
            with other data in json and add M2M link for field

        #2: If 'id' is not passed, this class will create a new object with data passed
            in json and create a M2M link

        #3: If 'link' & 'id' are passed, this class will add/remove object
            corresponding to id from M2M intermediate table data based on link
            value if true or false
        
        'id' here is the name of your model's primary key. If the primary key of model is named something 
        other than id, use that name.

    NOTE:   If there are nested serializers which further have serializer fields in
            them:
            1)If serializer has many=True, this class does not support such operation.

            2)If serializer does not have many=True and has further nested serializer,
            creation/updation logic will be needed to be handled in that serializer
            class's create/update method.

    If you want any nested serializer to be ignored by this class and you want to write
    custom implementation for create/update/validate, you can add pass serializer field
    names as list in 'ignore_serializer' Meta option. All fields with name in the list
    will be ignored but you need to override create/update method and pop the data from 
    validated_data before calling super.update or super.create 
    """

    def __init__(self, *args, **kwargs):
        self.serializer_classes = {}  # Stores nested serializer class types
        self.validated_nested_data = {}  # Stores validated data for nested serializers
        self.nested_errors = {}  # Stores validation errors for nested serializers
        self.complex_serializer_fields = []  # Stores field names of nested serializers who have further nested serializer fields
        self.ignore_serializer = getattr(self.Meta, "ignore_serializer", [])

        for field, field_object in self.fields.items():
            if (
                isinstance(field_object, serializers.BaseSerializer)
                and field not in self.ignore_serializer
                and not field_object.read_only
            ):
                if isinstance(field_object, serializers.ListSerializer):
                    child = field_object.child
                    for sub_field, sub_field_type in child.fields.items():
                        # Nested serializers with many=True & further nested serializer
                        # fields are not allowed
                        assert not isinstance(
                            sub_field_type, serializers.BaseSerializer
                        ), (
                            f"Field '{field}' is a ListSerializer which has further"
                            f" '{sub_field}' as a nested serializer. "
                            f"More than 1 level of nested serializer is not supported "
                            f"for serializer with many=True"
                        )

                    self.serializer_classes[field] = child.__class__
                else:
                    self._check_complex_serializers(field_object.fields, field)
                    self.serializer_classes[field] = field_object.__class__
        
        super().__init__(*args, **kwargs)

    def _check_complex_serializers(self, fields, parent_field):
        """
        Checks if a nested serializer is having further nested serializer
        This is only supported for nested serializers without many=True
        """
        for field, field_type in fields.items():
            if isinstance(field_type, serializers.BaseSerializer):
                self.complex_serializer_fields.append(parent_field)
    
    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        ret = {}
        errors = {}
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                if field.field_name in self.serializer_classes:
                    validated_value = self._validate_nested_serializer_field(field.field_name, primitive_value)
                else:
                    validated_value = field.run_validation(primitive_value)

                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                self.set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret
    
    def _validate_nested_serializer_field(self, field, data):
        if data:
            if isinstance(data, list):  # M2M field
                return self._validate_m2m_fields(data, field)

            elif isinstance(data, dict):  # FK or OneToOne field
                return self._validate_fk_onetoone_fields(data, field)

    def _get_serializer_object(self, data, class_type, action_type):
        """
        Returns serializer object corresponsing to class_type
        and action_type.
        This serializer object will be used for validation of input payload
        """
        serializer = class_type(data=data)
        ModelClass = serializer.Meta.model
        pk_field = ModelClass._meta.pk.name

        serializer_pk_field = serializers.PrimaryKeyRelatedField(
            queryset=ModelClass.objects.all()
        )
        link = serializers.BooleanField()

        if action_type == BaseWritableNestedSerializer.SerializerActions.LINK:
            serializer.fields.clear()
            serializer.fields[pk_field] = serializer_pk_field
            serializer.fields["link"] = link
        elif action_type == BaseWritableNestedSerializer.SerializerActions.UPDATE_M2M:
            serializer.partial = True
            serializer.fields[pk_field] = serializer_pk_field
        elif action_type == BaseWritableNestedSerializer.SerializerActions.UPDATE_O2O_FK:
            serializer.partial = True
        elif action_type == BaseWritableNestedSerializer.SerializerActions.CREATE:
            pass

        return serializer

    def _validate_m2m_fields(self, data, field):
        """
        Run validation for input payload of nested serializer
        with many=True.
        Input payload will be list of json objects.
        Eg. {
                field: [ #list
                    {
                        "key": "value
                    },
                    {
                        "key": "value
                    }
                ]
            }

        This will loop through each json passed inside the list for
        field, and validate it one by one. If there are any errors in
        any json passed inside list, they will be stored in 'nested_errors'
        dictionary. If there are no errors, validated data will be stored in
        'validated_nested_data' dictionary.
        """
        self.validated_nested_data[field] = []
        serializer_class = self.serializer_classes.get(field)
        pk_field = serializer_class.Meta.model._meta.pk.name
        errors = []
        ret = []
        for json in data:
            if "link" in json:  # Removing/Adding M2M link
                serializer = self._get_serializer_object(
                    data=json,
                    class_type=serializer_class,
                    action_type=BaseWritableNestedSerializer.SerializerActions.LINK,
                )
            else:
                if pk_field in json:  # Update scenario
                    serializer = self._get_serializer_object(
                        data=json,
                        class_type=serializer_class,
                        action_type=BaseWritableNestedSerializer.SerializerActions.UPDATE_M2M,
                    )

                else:  # create scenario
                    serializer = self._get_serializer_object(
                        data=json,
                        class_type=serializer_class,
                        action_type=BaseWritableNestedSerializer.SerializerActions.CREATE,
                    )

            is_valid = serializer.is_valid()
            if is_valid:
                ret.append(serializer.validated_data)
                self.validated_nested_data[field].append(serializer.validated_data)
            else:
                errors.append(serializer.errors)
                
        if errors:
            self.nested_errors[field] = errors
            raise ValidationError(errors)
        
        return ret

    def _validate_fk_onetoone_fields(self, data, field):
        """
        Run validation for nested serializer without many=True.
        Input payload will be json
        Eg. {
                field: { #json
                    "key": "value
                }
            }

        This function will create a serializer based on input payload and
        validate the json. If there is any errors in json, they will be
        stored in 'nested_errors' dictionary. If there are no errors,
        validated data will be stored in 'validated_nested_data' dictionary.
        """
        if "link" in data:  # Removing/Adding FK/OneToOne link
            serializer = self._get_serializer_object(
                data=data,
                class_type=self.serializer_classes.get(field),
                action_type=BaseWritableNestedSerializer.SerializerActions.LINK,
            )

        else:
            if getattr(self.instance, field, None):  # Update scenario
                serializer = self._get_serializer_object(
                    data=data,
                    class_type=self.serializer_classes.get(field),
                    action_type=BaseWritableNestedSerializer.SerializerActions.UPDATE_O2O_FK,
                )
                serializer.instance = getattr(self.instance, field)

            else:  # create scenario
                serializer = self._get_serializer_object(
                    data=data,
                    class_type=self.serializer_classes.get(field),
                    action_type=BaseWritableNestedSerializer.SerializerActions.CREATE,
                )
        is_valid = serializer.is_valid()
        if not is_valid:
            raise ValidationError(serializer.errors)
        
        self.validated_nested_data[field] = serializer.validated_data
        return serializer.validated_data

    def _validate_nested_objects(self, initial_data):
        """
        Run validation for nested serializers
        """
        for field in self.serializer_classes:
            data = initial_data.pop(field, None)
            if data:
                if isinstance(data, list):  # M2M field
                    self._validate_m2m_fields(data, field)

                elif isinstance(data, dict):  # FK or OneToOne field
                    self._validate_fk_onetoone_fields(data, field)

    def _update_or_create_m2m_fields(self, instance, field, value):
        """
        Create, update & Link/Unlink ManyToMany field data
        """
        related_manager = getattr(instance, field)
        serializer_class = self.serializer_classes.get(field)
        pk_field = serializer_class.Meta.model._meta.pk.name
        for json in value:
            if "link" in json:
                if json.get("link"):  # link = True
                    related_manager.add(json.get(pk_field))
                else:  # link = False
                    related_manager.remove(json.get(pk_field))
            else:
                if pk_field in json:  # update object with pk = id
                    object = json.pop(pk_field)
                    self.update_nested(object, json)
                    related_manager.add(object)
                else:  # create new object and add M2M relation
                    model = serializer_class.Meta.model
                    object = self.create_nested(json, model)
                    related_manager.add(object)

    def _update_or_create_onetoone_fk_fields(self, instance, field, value):
        """
        Create, update & Link/Unlink OneToOne field & ForeignKey data
        """
        serializer_class = self.serializer_classes.get(field)
        pk_field = serializer_class.Meta.model._meta.pk.name
        if "link" in value:
            if value.get("link"):
                setattr(instance, field, value.get(pk_field))
            else:
                setattr(instance, field, None)
            instance.save()
        else:
            if field in self.complex_serializer_fields:
                # If field is a serializer that has another nested serialzier,
                # handle creation and update from serializer itself.
                partial = True if getattr(instance, field, None) else False
                serializer = serializer_class(
                    getattr(instance, field, None),
                    data=self.initial_data.get(field),
                    partial=partial,
                )
                serializer.is_valid(raise_exception=True)
                object = serializer.save()
                setattr(instance, field, object)
                instance.save()
                return

            if getattr(instance, field):
                object = getattr(instance, field)
                self.update_nested(object, value)
            else:
                model = self.serializer_classes.get(field).Meta.model
                object = self.create_nested(value, model)
                setattr(instance, field, object)
                instance.save()

    def _update_or_create_nested_objects(self, instance, validated_data):
        """
        Create or update nested serializer's data
        """
        for field in self.serializer_classes.keys():
            if field in validated_data:
                value = validated_data.pop(field)
                if isinstance(value, list):  # M2M fields
                    self._update_or_create_m2m_fields(instance, field, value)

                elif isinstance(value, dict):  # OneToOne & ForeignKey fields
                    self._update_or_create_onetoone_fk_fields(instance, field, value)

    def update(self, instance, validated_data):
        ignored_data = {}
        for field in self.ignore_serializer:
            if field in validated_data:
                ignored_data[field] = validated_data.pop(field)
            
        self._update_or_create_nested_objects(instance, validated_data)
        instance = self.update_nested(instance, validated_data)
        validated_data.update(ignored_data)
        return instance

    def create(self, validated_data):
        ignored_data = {}
        for field in self.ignore_serializer:
            if field in validated_data:
                ignored_data[field] = validated_data.pop(field)
        
        nested_data = {}
        for field in self.serializer_classes.keys():
            if field in validated_data:
                nested_data[field] = validated_data.pop(field)

        instance = self.create_nested(validated_data)
        self._update_or_create_nested_objects(instance, nested_data)
        validated_data.update(ignored_data)
        return instance

    def create_nested(self, validated_data, model=None):
        """
        Creates new model object. If model argument is passed,
        object of passed model will be created else, current
        serializer's Meta.model object will be created
        with validated_data
        """
        ModelClass = model if model else self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                "Got a `TypeError` when calling `%s.%s.create()`. "
                "This may be because you have a writable field on the "
                "serializer class that is not a valid argument to "
                "`%s.%s.create()`. You may need to make the field "
                "read-only, or override the %s.create() method to handle "
                "this correctly.\nOriginal exception was:\n %s"
                % (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb,
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    def update_nested(self, instance, validated_data):
        """
        Update the instance object values with the values
        provided in validated_data
        """
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    class SerializerActions(Enum):
        LINK = "link"
        CREATE = "create"
        UPDATE_M2M = "update-m2m"
        UPDATE_O2O_FK = "update-o2o-fk"

class WritableNestedSerializer(BaseWritableNestedSerializer):
    pass