from collections import (
    OrderedDict,
    defaultdict,
)

from django.db.models import (
    Q,
)
from m3_gar.models import (
    AddhouseTypes,
    AddrObj,
    AddrObjParams,
    AddrObjTypes,
    Apartments,
    ApartmentsParams,
    ApartmentTypes,
    CarplacesParams,
    Houses,
    HousesParams,
    HouseTypes,
    ParamTypes,
    ReestrObjects,
    Rooms,
    RoomsParams,
    RoomTypes,
    Steads,
    SteadsParams,
)
from m3_gar.models.hierarchy import (
    AdmHierarchy,
    Hierarchy,
    MunHierarchy,
)
from m3_rest_gar.consts import (
    GAR_DATE_MAX,
)
from rest_framework import (
    serializers,
)
from rest_framework.fields import (
    SkipField,
    empty,
)
from rest_framework.relations import (
    PKOnlyObject,
)


class ReestrObjectsSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений об адресном элементе в части его идентификаторов
    """
    class Meta:
        model = ReestrObjects
        fields = '__all__'


class HierarchySerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор сведений по иерархии
    """
    objectid = ReestrObjectsSerializer()
    parentobjid = ReestrObjectsSerializer()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Hierarchy
        fields = '__all__'

    def get_has_children(self, obj):
        """
        Возвращает boolean признак наличия потомков

        Args:
            obj: объект AdmHierarchy/MunHierarchy
        """
        if hasattr(obj, 'has_children_in_cache'):
            res = obj.has_children_in_cache
        else:
            res = obj.has_children

        return res


class MunHierarchySerializer(HierarchySerializer):
    """
    Сериализатор сведений по иерархии в муниципальном делении
    """
    class Meta:
        model = MunHierarchy
        fields = '__all__'


class AdmHierarchySerializer(HierarchySerializer):
    """
    Сериализатор сведений по иерархии в административном делении
    """
    class Meta:
        model = AdmHierarchy
        fields = '__all__'


class ParamTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по типу параметра
    """
    class Meta:
        model = ParamTypes
        fields = '__all__'


class ParamListSerializer(serializers.ListSerializer):
    """
    Сериализатор списка сведений о классификаторе параметров адресообразующих
    элементов и объектов недвижимости
    """
    def to_representation(self, data):
        if not isinstance(data, list):
            data = data.filter(
                enddate=GAR_DATE_MAX,
            ).select_related(
                'typeid',
            )

        return super().to_representation(data)


class ParamSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений о классификаторе параметров адресообразующих
    элементов и объектов недвижимости
    """
    typeid = ParamTypesSerializer()

    class Meta:
        fields = '__all__'
        list_serializer_class = ParamListSerializer


class AddrObjParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = AddrObjParams


class ApartmentsParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = ApartmentsParams


class CarplacesParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = CarplacesParams


class HousesParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = HousesParams


class RoomsParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = RoomsParams


class SteadsParamsSerializer(ParamSerializer):

    class Meta(ParamSerializer.Meta):
        model = SteadsParams


class AddrObjTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по типам адресных объектов
    """
    class Meta:
        model = AddrObjTypes
        fields = '__all__'


class HierarchicalObjSerializerMixin(
    metaclass=serializers.SerializerMetaclass
):
    """
    Примесь для сериализаторов объектов содержащих сведения об иерархии.
    """
    hierarchy = serializers.SerializerMethodField()

    def get_hierarchy(self, obj):
        data = {}

        for name, model in Hierarchy.get_shortname_map().items():
            if hasattr(self, f'{name}_cache'):
                hierarchy_instance = getattr(self, f'{name}_cache', {}).get(obj.objectid_id)
            else:
                hierarchy_instance = model.objects.filter(
                    objectid=obj.objectid,
                    enddate=GAR_DATE_MAX,
                    isactive=True,
                ).select_related(
                    'objectid',
                    'parentobjid',
                ).first()

            hierarchy_serializer = globals()[f'{model.__name__}Serializer']

            if hierarchy_instance and hierarchy_serializer:
                if hasattr(self, f'{name}_has_children_cache'):
                    hierarchy_instance.has_children_in_cache = (
                        obj.objectid_id in getattr(self, f'{name}_has_children_cache')
                    )

                data[name] = hierarchy_serializer(hierarchy_instance).data

        return data


class AddrObjSerializer(
    HierarchicalObjSerializerMixin,
    serializers.ModelSerializer
):
    """
    Сериализатор сведений классификатора адресообразующих элементов
    """
    params = AddrObjParamsSerializer(many=True)
    type_full_name = serializers.SerializerMethodField()

    # На момент описания моделей AddrObjTypes никак не связывается с AddrObj
    # Существующее поле AddrObj.typename - текстовое представление (ул, пер, г, и т.п.)
    # ??? = AddrObjTypesSerializer()

    def __init__(self, instance=None, data=empty, **kwargs):
        if isinstance(instance, list):
            reestr_object_ids = list()
            unique_addr_obj_types = set()
            for obj in instance:
                reestr_object_ids.append(obj.objectid_id)
                unique_addr_obj_types.add((obj.typename, obj.level))

            self._set_addr_obj_types_cache(unique_addr_obj_types)
            self._set_addr_obj_params_cache(reestr_object_ids)
            self._set_hierarchy_cache(reestr_object_ids)
            self._set_has_children_cache(reestr_object_ids)

        super().__init__(instance, data, **kwargs)

    def _set_addr_obj_types_cache(self, unique_addr_obj_types):
        """
        Заполняет кеш AddrObjTypes

        Args:
            unique_addr_obj_types: множество кортежей вида
                ('Краткое наименование типа объекта', 'Уровень адресного объекта')
        """
        obj_types_filter = Q()
        for typename, level in unique_addr_obj_types:
            obj_types_filter |= Q(shortname=typename, level=level)

        self.addr_obj_types_cache = {}
        add_obj_types_query = AddrObjTypes.objects.filter(obj_types_filter, isactive=True)
        for row in add_obj_types_query:
            self.addr_obj_types_cache[(row.shortname, row.level)] = row

    def _set_addr_obj_params_cache(self, reestr_object_ids):
        """
        Заполняет кеш AddrObjParams

        Args:
            reestr_object_ids: список айдишников ReestrObjects
        """
        self.addr_obj_params_cache = defaultdict(list)
        addrobjparams_query = AddrObjParams.objects.filter(
            objectid__in=reestr_object_ids,
            enddate=GAR_DATE_MAX,
        ).select_related(
            'typeid',
        )
        for row in addrobjparams_query:
            self.addr_obj_params_cache[row.objectid].append(row)

    def _set_hierarchy_cache(self, reestr_object_ids):
        """
        Заполняет кеш AdmHierarchy/MunHierarchy

        Args:
            reestr_object_ids: список айдишников ReestrObjects
        """
        for name, model in Hierarchy.get_shortname_map().items():
            data = {}
            hierarchy_query = model.objects.filter(
                objectid_id__in=reestr_object_ids,
                enddate=GAR_DATE_MAX,
                isactive=True,
            ).select_related(
                'objectid',
                'parentobjid',
            )

            for row in hierarchy_query:
                data[row.objectid_id] = row

            setattr(self, f'{name}_cache', data)

    def _set_has_children_cache(self, reestr_object_ids):
        """
        Заполняет кеш по признаку "Наличие потомков"

        Args:
            reestr_object_ids: список айдишников ReestrObjects
        """
        level_dict = defaultdict(list)
        level_query = ReestrObjects.objects.filter(
            objectid__in=reestr_object_ids,
        ).values_list(
            'objectid',
            'levelid_id',
            named=True
        )

        for row in level_query:
            level_dict[row.levelid_id].append(row.objectid)

        q_filter = Q()
        for level, objectid_ids in level_dict.items():
            q_filter |= Q(
                objectid__levelid=level + 1,
                parentobjid_id__in=objectid_ids,
            )

        for name, model in Hierarchy.get_shortname_map().items():
            data = set(
                model.objects.filter(
                    q_filter,
                    isactive=True,
                ).distinct('parentobjid_id').values_list('parentobjid_id', flat=True)
            )
            setattr(self, f'{name}_has_children_cache', data)

    def to_representation(self, instance):
        """
        Метод переопределён для получения записей из кеша

        Args:
            instance: объект AddrObj
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                if (
                    hasattr(self, 'addr_obj_params_cache') and
                    hasattr(field, 'child') and
                    field.child.__class__ == AddrObjParamsSerializer
                ):
                    attribute = self.addr_obj_params_cache[instance.objectid_id]
                else:
                    attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def get_type_full_name(self, obj):
        """
        Возвращает полное имя типа объекта

        Args:
            obj: объект AddrObj
        """
        addr_obj_type = getattr(self, 'addr_obj_types_cache', {}).get((obj.typename, int(obj.level)))
        if addr_obj_type:
            result = addr_obj_type.name.lower()
        else:
            result = obj.type_full_name.lower()

        return result

    class Meta:
        model = AddrObj
        fields = '__all__'


class HouseTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по типам домов
    """
    class Meta:
        model = HouseTypes
        fields = '__all__'


class AddhouseTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по дополнительным типам домов
    """
    class Meta:
        model = AddhouseTypes
        fields = '__all__'


class HousesSerializer(
    HierarchicalObjSerializerMixin,
    serializers.ModelSerializer
):
    """
    Сериализатор сведений по номерам домов улиц городов и населенных пунктов
    """
    params = HousesParamsSerializer(many=True)
    housetype = HouseTypesSerializer()
    addtype1 = AddhouseTypesSerializer()
    addtype2 = AddhouseTypesSerializer()

    class Meta:
        model = Houses
        fields = '__all__'


class SteadsSerializer(
    HierarchicalObjSerializerMixin,
    serializers.ModelSerializer
):
    """
    Сериализатор сведений по земельным участкам
    """

    params = SteadsParamsSerializer(many=True)

    class Meta:
        model = Steads
        fields = '__all__'


class ApartmentTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по типам помещений
    """
    class Meta:
        model = ApartmentTypes
        fields = '__all__'


class ApartmentsSerializer(HierarchicalObjSerializerMixin, serializers.ModelSerializer):
    """
    Сериализатор сведений по помещениям
    """
    params = ApartmentsParamsSerializer(many=True)
    aparttype = ApartmentTypesSerializer()

    class Meta:
        model = Apartments
        fields = '__all__'


class RoomTypesSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по типам комнат
    """
    class Meta:
        model = RoomTypes
        fields = '__all__'


class RoomsSerializer(serializers.ModelSerializer):
    """
    Сериализатор сведений по комнатам
    """
    params = RoomsParamsSerializer(many=True)
    roomtype = RoomTypesSerializer()

    class Meta:
        model = Rooms
        fields = '__all__'
