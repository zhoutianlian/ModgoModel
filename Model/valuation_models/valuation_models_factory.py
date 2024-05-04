from Model.valuation_models.financial_valuation.asset_valuation import AssetFin
from Model.valuation_models.financial_valuation.samulson_valuation import SamulsonFin
from Model.valuation_models.financial_valuation.market import MktMethodFin
from Model.valuation_models.normal_valuation.market import Market_Mtd
from Model.valuation_models.normal_valuation.cost_method import Cost
from Model.valuation_models.normal_valuation.eva import EVA
from Model.valuation_models.normal_valuation.rim import RIM
from Model.valuation_models.normal_valuation.nopat import NOPAT
from Model.valuation_models.normal_valuation.apv import APV
from Model.valuation_models.normal_valuation.samuelson_lite import Samuelson_Normal_Lite
from Model.valuation_models.normal_valuation.samuelson_standard import Samuelson_Normal_Standard
from Model.valuation_models.real_estate_valuation.real_estate import RealEstate
from Model.valuation_models.venture_investment.ventureinvestment_model_normal import Normal_VI
from Model.valuation_models.venture_investment.ventureinvestment_model_samuelson import Samuelson_VI
from Config.global_V import ValuationModels


class ValuationModelsFactory():
    def choose_valuation_model(self,name):
        if name==ValuationModels.FIN_MKT:
            return MktMethodFin()
        elif name==ValuationModels.FIN_SAM:
            return SamulsonFin()
        elif name==ValuationModels.FIN_ASS:
            return AssetFin()
        elif name==ValuationModels.REAL_ESTATE:
            return RealEstate()
        elif name==ValuationModels.NOR_COST:
            return Cost()
        elif name==ValuationModels.NOR_EVA:
            return EVA()
        elif name==ValuationModels.NOR_MKT:
            return Market_Mtd()
        elif name==ValuationModels.NOR_NOPAT:
            return NOPAT()
        elif name==ValuationModels.NOR_RIM:
            return RIM()
        elif name==ValuationModels.NOR_SAM_LITE:
            return Samuelson_Normal_Lite()
        elif name==ValuationModels.NOR_SAM_STANDARD:
            return Samuelson_Normal_Standard()
        elif name==ValuationModels.VI_NOR:
            return Normal_VI()
        elif name==ValuationModels.VI_SAM:
            return Samuelson_VI()
        elif name == ValuationModels.NOR_APV:
            return APV()


