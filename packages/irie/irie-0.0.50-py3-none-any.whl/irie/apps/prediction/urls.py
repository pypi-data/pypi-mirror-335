#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
from django.urls import re_path
from .views import new_prediction, asset_predictors, predictor_profile, predictor_upload, asset_map

urlpatterns = [
    re_path("^inventory/[0-9 A-Z-]*/predictors/new",   new_prediction),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/predictors/(?P<preid>[0-9 A-Z-]{1,})", predictor_profile),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/predictors/create/map/$", asset_map),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/map/$",                   asset_map),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/predictors/create/$",     predictor_upload),
    re_path("^inventory/(?P<calid>[0-9 A-Z-]*)/predictors/",             asset_predictors, name="asset_predictors")
]
