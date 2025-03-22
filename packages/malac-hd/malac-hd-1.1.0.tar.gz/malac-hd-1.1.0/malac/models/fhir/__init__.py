from malac.models.fhir import r4, r5, utils

for mod in [r4, r5]:
    mod.Resource.exportJsonAttributes = utils.exportJsonAttributesResource
    mod.ResourceContainer.exportJsonResult = utils.exportJsonResultResourceContainer
    mod.Narrative.exportJsonResult = utils.exportJsonResultNarrative
    mod.Element.exportJsonResult = utils.exportJsonResultElement
    mod.date.exportJsonAttributes = utils.exportJsonAttributesDateDateTime
    mod.dateTime.exportJsonAttributes = utils.exportJsonAttributesDateDateTime
