Climate Health Analytics Platform (CHAP)
==============================================================

CHAP is a platform for forecasting and for assessing forecasts of climate-sensitive health outcomes.
In the early phase, the focus is on vector-borne diseases like malaria and dengue.

The platform can perform data parsing, data integration, forecasting based on any of
multiple supported models, automatic brokering of compatible models for a given prediction context and robust forecast assessment and method comparison.

This documentation contains technical information about installing and using CHAP. For more general information about the project, we refer to `the CHAP project wiki <https://github.com/dhis2-chap/chap-core/wiki>`_. 

----

All pages
----------

The following is an overview of all pages in the documentation:

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Installation and getting started

   installation/installation
   changelog


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Using the Predictions App with CHAP and DHIS2

   prediction-app/*


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Using CHAP as a CLI Tool

   chap-cli/*


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Using CHAP as a Python library

   python-api/*


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Integrating external or custom models with CHAP

   external_models/making_external_models_compatible
   external_models/developing_custom_models
   external_models/external_model_specification
   external_models/running_external_models
   external_models/integrating_external_models_with_dhis2
   external_models/wrapping_gluonts


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contributor guide 

   contributor/getting_started
   contributor/windows_contributors
   contributor/code_overview
   contributor/testing
   contributor/writing_building_documentation
   contributor/code_guidelines
   contributor/r_docker_image
