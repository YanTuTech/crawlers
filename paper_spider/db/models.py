from playhouse.sqlite_ext import *

db = SqliteExtDatabase('paper_new.db')

class BaseModel(Model):
    class Meta:
        database = db

'''json
journals = [
    {
        "name": "Journal of Materials Chemistry A",
        "abrv_name": "J MATER CHEM A",
        "ssin": "2050-7488",
        "e_ssin": "2050-7496",
        "impact_factor": 11.301,
        "self_ciation_ratio": 0.088,
        "jcr_cat": {
            "name": "Materials Science",
            "code": "Q1"
        },
        "jcr_sub": [
            "General Materials Science",
            "General Chemistry",
            "Renewable Energy, Sustainability and the Environment"
        ],
        "cas_base_cat": {
            "name": "工程技术",
            "code": "1区"
        },
        "case_base_sub": [
            {
                "name": "物理化学",
                "en_name": "CHEMISTRY, PHYSICAL",
                "code": "2区"
            },
            {
                "name": "能源与燃料",
                "en_name": "ENERGY & FUELS",
                "code": "1区"
            },
            {
                "name": "材料科学：综合",
                "en_name": "MATERIALS SCIENCE, MULTIDISCIPLINARY",
                "code": "2区"
            },
        ],
        "case_base_top": true,
        "case_base_review": false,
        "cas_new_cat": {
            "name": "材料科学",
            "code": "2区"
        },
        "case_new_sub": [
            {
                "name": "物理化学",
                "en_name": "CHEMISTRY, PHYSICAL",
                "code": "2区"
            },
            {
                "name": "能源与燃料",
                "en_name": "ENERGY & FUELS",
                "code": "2区"
            },
            {
                "name": "材料科学：综合",
                "en_name": "MATERIALS SCIENCE, MULTIDISCIPLINARY",
                "code": "2区"
            },
        ],
        "case_new_top": true,
        "case_new_review": false,
    }
]
'''


class JCRCategory(BaseModel):
    name = CharField(unique=True)
    code = CharField()


class JCRSubCategory(BaseModel):
    name = CharField(unique=True)


class CASBaseCategory(BaseModel):
    name = CharField(unique=True)
    code = CharField()


class CASBaseSubCategory(BaseModel):
    name = CharField(unique=True)
    en_name = CharField()
    code = CharField()


class CASNewCategory(BaseModel):
    name = CharField(unique=True)
    code = CharField()


class CASNewSubCategory(BaseModel):
    name = CharField(unique=True)
    en_name = CharField()
    code = CharField()


class Journal(BaseModel):
    name = CharField()
    abrv_name = CharField()
    impact_factor = FloatField()
    ssin = CharField(unique=True)
    e_ssin = CharField()
    self_citation_ratio = FloatField() # 2019-2020
    jcr_cat = ForeignKeyField(JCRCategory, null=True)
    cas_base = ForeignKeyField(CASBaseCategory, null=True)
    cas_base_top = BooleanField()
    cas_base_review = BooleanField()
    cas_new = ForeignKeyField(CASNewCategory, null=True)
    cas_new_top = BooleanField()
    cas_new_review = BooleanField()


class JCRSubCatRel(BaseModel):
    sub_cat = ForeignKeyField(JCRSubCategory)
    journal = ForeignKeyField(Journal)


class CASBaseSubCatRel(BaseModel):
    journal = ForeignKeyField(Journal)
    cas_base_sub = ForeignKeyField(CASBaseSubCategory)


class CASNewSubCatRel(BaseModel):
    journal = ForeignKeyField(Journal)
    cas_new_sub = ForeignKeyField(CASNewSubCategory)


all_models = [Journal, JCRCategory, JCRSubCategory, JCRSubCatRel, CASBaseCategory, CASBaseSubCatRel, CASBaseSubCategory, CASNewCategory, CASNewSubCatRel, CASNewSubCategory]
