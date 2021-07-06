**AIR-DRF-RELATION**

# Table of Contents

1. [Instalation](#instalation)
2. [About](#about)
3. [RelatedField](#relatedfield)
    1. [pk_only](#pk_only)
    2. [hidden](#hidden)
4. [AirModelSerializer](#airmodelserializer)
    1. [user](#user)
    2. [extra_kwargs](#extra_kwargs)
    3. [hidden_fields](#hidden_fields)
    4. [Kwargs by actions](#kwargs-by-actions)
        1. [action_read_only_fields](#action_read_only_fields)
        2. [action_hidden_fields](#action_hidden_fields)
        3. [action_extra_kwargs](#action_extra_kwargs)
    5. [Filter nested querysets](#filter_nested_querysets)
5. [Nested save objects](#nested-save-objects)
    1. [Saving nested objects without NestedFactory](#saving-nested-objects-without-nestedfactory) 
    2. [Saving nested objects with NestedFactory](#saving-nested-objects-with-nestedfactory)
    3. [Using NestedFactory in AirModelSerializer](#using-nestedfactory-in-airmodelserializer)

# Instalation

`$ pip install air-drf-relation`

# About

Add folder **models** in src. Add a file to the directory that will contain the model, for example **user**.

# RelatedField

Used to extend the functionality of the `PrimaryKeyRelatedField`

```python
class BookSerializer(ModelSerializer):
    # author = PrimaryKeyRelatedField(queryset=Author.objects) - default usage
    author = RelatedField(AuthorSerializer)
    city = RelatedField(AuthorSerializer)

    class Meta:
        model = Book
        fields = ('uuid', 'name', 'author', 'city')
```

`RelatedField` allows you to get not only pk but also an object with pk, which will be searched.
```json
{
    "name": "demo",
    "author": { 
        "id": 1
    },
    "city": 1
}
```
## pk_only
Automatically RelatedField returns a serialized object. If you only want to use pk, you must specify the `pk_only` key.

```python
author = RelatedField(AuthorSerializer, pk_only=True)
```

## hidden
Hidden fields are not used for serialization and validation. The data will be returned without fields. Usually used together in `AirModelSerializer`

```python
author = RelatedField(AuthorSerializer, hidden=True)
```

## Important
You cannot use `hidden` and `pk_only` in ModelSerializer and with extra_kwargs

# AirModelSerializer

Used to extend the functionality of the `ModelSerializer`

```python
class BookSerializer(AirModelSerializer): # full example
    author = RelatedField(AuthorSerializer)
    city = RelatedField(AuthorSerializer)

    class Meta:
        model = Book
        fields = ('uuid', 'name', 'author', 'city')
        hidden_fields = ()
        read_only_fields = () # default read_only_fields
        extra_kwargs = {} # default extra_kwargs with support custom keys
        action_read_only_fields = {
            'create': {},
            '_': {} # used for other actions
        },
        action_hidden_fields = {
            'create': (),
            '_': ()
        }
        action_extra_kwargs = {
            'list': {},
            '_': {}
        }
        nested_save_fields = ()
```

## user
User is automatically put from the `request` if available. You can also set the user manually.

```python
class DemoSerializer(AirModelSerializer):
    class Meta:
        fields = ('id', 'name')
    
    validate_name(self, value):
        if not self.user:
            return None
        return value
```
Manually set user.
```python
serializer = DemoSerializer(data={'name': 'demo'}, user=request.user)
```

## extra_kwargs
Extends the standard work with `extra_kwargs` by adding work with additional attributes. You can also transfer `extra_kwargs` manually.

```python
class BookSerializer(AirModelSerializer):
    author = RelatedField(AuthorSerializer)
    
    class Meta:
        fields = ('id', 'name', 'author')
        extra_kwargs = {
            'author': {'pk_only': True},
            'name': {'hidden': True}
        }
```
## hidden_fields
Hides fields for validation and seralization.
```python
class BookSerializer(AirModelSerializer):
    class Meta:
        fields = ('id', 'name', 'author')
        hidden_fields = ('name', 'author')
```
## Kwargs by actions
Kwargs by actions is used only when the event. You can pass acions separated by `,`.
For events that don't match, you can use `_` key. It is used if action **is passed**.
Action is set automatically from the ViewSet, or it can be passed manually.

```python
class DemoViewSet(ModelViewSet):
    queryset = Demo.objects.all()
    serializer_class = DemoSerializer
    
    def perform_create(serializer, request):
        action = serializer.action # action is 'create'
        serializer.save()
    
    @action(methods=['POST'], detail=False)
    def demo_action(self, request):
        serializer = self.get_serializer_class()
        action = serializer.action # action is 'demo_action'
```

Manually set action.
```python
serializer = DemoSerializer(data={'name': 'demo'}, action='custom_action')
action = serializer.action # action is 'custom_action'
```

### action_read_only_fields
Sets `read_only_fields` by action in serializer.

```python
class BookSerializer(AirModelSerializer):
    class Meta:
        fields = ('id', 'name', 'author')
        action_read_only_fields = {
            'create,update': ('name', 'author')
        }
```

### action_hidden_fields
Sets `hidden_fields` by action in serializer.

```python
class BookSerializer(AirModelSerializer):
    class Meta:
        fields = ('id', 'name', 'author')
        action_hidden_fields = {
            'custom_action': ('author', ),
            '_': ('id', )
        }
```

### action_extra_kwargs
Expand `extra_kwargs` by action in serializer.

```python
class BookSerializer(AirModelSerializer):
    author = RelatedField(AuthorSerializer, pk_only=True, null=True)
    
    class Meta:
        fields = ('id', 'name', 'author')
        action_extra_kwargs = {
            'create,custom_update': {
                'author': {'pk_only': False, 'null'=True}
            }
        }
```

## Filter nested querysets
AirModelSerializer allows you to filter the queryset by nested fields.
```python
class BookSerializer(AirModelSerializer):
    city = RelatedField(CitySerializer, queryset_function_name='custom_filter')

    def queryset_author(self, queryset):
        return queryset.filter(active=True, created_by=self.user)

    def filter_city_by_active(self, queryset):
        return queryset.filter(active=True)

    class Meta:
        model = Book
        fields = ('uuid', 'name', 'author', 'city')
```

# Nested save objects
You can use the `NestedFactory` functionality to easily create or update objects by nested fields. NestedFactory stores primary keys by **default**. But you can delete objects and create new ones every time.

**Only use NestedFactory in simple cases!**

## Saving nested objects without NestedFactory

```python
class CabinetSerializer(ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ('id', 'name', 'code') # you should hide or set read_only on 'school' field
        

class SchoolDefaultNestedSerializer(ModelSerializer):
    cabinets = CabinetSerializer(many=True)

    class Meta:
        model = School
        fields = ('id', 'name', 'cabinets')

    def create(self, validated_data):
        cabinets = validated_data.pop('cabinets', [])
        instance = School.objects.create(**validated_data)
        for el in cabinets:
            Cabinet.objects.create(**el, school=instance)
        return instance

    def update(self, instance: School, validated_data):
        cabinets = validated_data.pop('cabinets', [])
        instance.cabinets.all().delete()
        instance.__dict__.update(validated_data)
        instance.save()
        for el in cabinets:
            Cabinet.objects.create(**el, school=instance)
        return instance
```

## Saving nested objects with NestedFactory

```python
class CabinetSerializer(ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ('id', 'name', 'code', 'school') # 'school' field is required


class SchoolCustomNestedSerializer(ModelSerializer):
    cabinets = CabinetSerializer(many=True)

    class Meta:
        model = School
        fields = ('id', 'name', 'cabinets')

    def save_nested(self, validated_data, instance=None):
        factory = NestedSaveFactory(serializer=self, nested_save_fields=['cabinets'])
        factory.set_data(validated_data=validated_data, instance=instance)
        return factory.save_instance().save_nested_fields().instance

    def create(self, validated_data):
        return self.save_nested(validated_data=validated_data)

    def update(self, instance, validated_data):
        return self.save_nested(validated_data=validated_data, instance=instance)
```

## Using NestedFactory in AirModelSerializer
```python
class CabinetSerializer(ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ('id', 'name', 'code', 'school') # 'school' field is required


class SchoolAutoNestedSerializer(ModelSerializer):
    cabinets = CabinetSerializer(many=True)

    class Meta:
        model = School
        fields = ('id', 'name', 'cabinets')
        nested_save_fields = ('cabinets',)
```
