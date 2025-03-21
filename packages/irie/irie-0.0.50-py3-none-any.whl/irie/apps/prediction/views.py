#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   This module implements the "Configure Predictors" page
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
import os
import json
import veux
import uuid
import base64

from django.shortcuts import HttpResponse
from django.template import loader, TemplateDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from django.shortcuts import render

from irie.apps.site.view_utils import raise404
from irie.apps.inventory.models import Asset
from irie.apps.prediction.predictor import PREDICTOR_TYPES
from irie.apps.prediction.models import PredictorModel
from .forms import PredictorForm

@login_required(login_url="/login/")
def new_prediction(request):
    context = {}

    page_template = "form-submission.html"
    context["segment"] = page_template
    html_template = loader.get_template("prediction/" + page_template)
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def asset_predictors(request, calid):

    context = {"segment": "inventory"}

    context["runners"] = list(reversed([
        {
            "schema": json.dumps(cls.schema),
            "name":   cls.__name__,
            "title":  cls.schema.get("title", "NO TITLE"),
            "protocol":   key
        }
        for key,cls in PREDICTOR_TYPES.items() if key
    ]))


    try:
        context["asset"] = Asset.objects.get(calid=calid)

    except Asset.DoesNotExist:
        return HttpResponse(
                loader.get_template("site/page-404-sidebar.html").render(context, request)
               )

    html_template = loader.get_template("prediction/asset-predictors.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def predictor_profile(request, calid, preid):

    context = {}
    html_template = loader.get_template("prediction/predictor-profile.html")
    context["segment"] = "inventory"

    try:
        asset = Asset.objects.get(calid=calid)
    except Asset.DoesNotExist:
        return raise404(request, context)

    try:
        predictor = PredictorModel.objects.get(pk=int(preid))
    except ObjectDoesNotExist:
        return raise404(request, context)

    context["asset"] = asset
    context["predictor"] = PREDICTOR_TYPES[predictor.protocol](predictor)

    try:
        return HttpResponse(html_template.render(context, request))

    except TemplateDoesNotExist:
        context["rendering"] = None
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def asset_map(request, calid):
    """
    See also https://www.f4map.com/
    """
    r200 = loader.get_template("inventory/asset-on-map.html")
    r400 = loader.get_template("site/page-400.html")
    asset = Asset.objects.get(calid=calid)
    context = {
        "asset": asset,
        "viewer": "three",
        "location": json.dumps(list(reversed(list(asset.coordinates)))),
    }

    if request.method == "GET":
        context["render_src"] = asset.rendering

    elif request.method == "POST":
        from openbim.csi import load, create_model, collect_outlines
        # context["offset"] = json.dumps(list(reversed(list(asset.coordinates))))
        context["rotate"] = "[0, 0, 0]"
        context["scale"]  = 1/3.2808 # TODO

        uploaded_file = request.FILES.get('config_file')

        try:
            csi = load((str(line.decode()).replace("\r\n","\n") for line in uploaded_file.readlines()))
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=400)

        try:
            model = create_model(csi, verbose=True)
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=400)


        outlines = collect_outlines(csi, model.frame_tags)
        artist = veux.render(model, canvas="gltf", vertical=3,
                                reference={"frame.surface", "frame.axes"},
                                model_config={"frame_outlines": outlines})

        glb = artist.canvas.to_glb()
        glb64 = base64.b64encode(glb).decode("utf-8")
        context["render_glb"] = f"data:application/octet-stream;base64,{glb64}"


    try:
        return HttpResponse(r200.render(context, request))

    except Exception as e:
        r500 = loader.get_template("site/page-500.html")
        return HttpResponse(r500.render({"message": str(e)}, request), status=500)




@login_required(login_url="/login/")
def predictor_upload(request, calid):

    asset = Asset.objects.get(calid=calid)
    html_template = loader.get_template("prediction/predictor-upload.html")
    r400 = loader.get_template("site/page-400.html")
    context = {
        "asset": asset,
        "segment": "inventory",
        "viewer": "babylon",
        "offset": json.dumps(list(reversed(list(asset.coordinates)))),
    }

    if request.method == "POST":
        from openbim.csi import load, create_model, collect_outlines
        form = PredictorForm(request.POST, request.FILES)

        uploaded_file = request.FILES.get('config_file')

        try:
            csi = load((str(line.decode()).replace("\r\n","\n") for line in uploaded_file.readlines()))
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=400)

        model = create_model(csi, verbose=True)

        # Generate the .glb file using veux
        outlines = collect_outlines(csi, model.frame_tags)
        artist = veux.create_artist(model, canvas="gltf", vertical=3,
                             model_config={"frame_outlines": outlines}
        )
        artist.draw_surfaces()
        glb = artist.canvas.to_glb()

        if request.POST.get("action") == "commit":
            if not form.is_valid():
                return HttpResponse(json.dumps({"error": "Invalid form data"}), status=400)
            predictor = PredictorModel()
            predictor.active = False
            predictor.asset = asset
            predictor.name = form.cleaned_data['name']
            predictor.description = "empty"

            predictor.render_file.save(f"{uuid.uuid4()}.glb", ContentFile(glb), save=True)
            predictor.save()

        context["form"] = form

    else: # probably a GET
        context["form"] = PredictorForm()


    try:
        return HttpResponse(html_template.render(context, request))
        # return render(request, "prediction/predictor-upload.html", {"form": form})

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render({}, request))


