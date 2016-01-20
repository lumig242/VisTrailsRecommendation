# Scientific Workflow Recommendation
As current satellite measurements rapidly magnify the accumulation of more than 40 years of scientific knowledge, new discoveries increasingly require collaborative integration and adaptation of various data-driven software components (tools). In recent years, scientists have learned how to codify tools into reusable software modules that can be chained into multi-step executable workflows. However, although computing technologies continue to improve, adoption via the sharing and reuse of modules and workflows remains a big challenge.

This project at Carnegie Mellon University aims to tackle this challenge from a novel angle, to study how to leverage peer scientists’ best practice to help facilitate the discovery and reuse of Earth science modules developed by others.

This plugin is built on top of the latest version of VisTrails.


## To Start

The following 4 steps describe the detailed procedure how to install and run our software.

Note that our installation package is considerate to automatically help you set up the entire 

running environment including upgrading your python environment.

Operating System: Ubuntu 12.04 LTS

I. Machine Environmental Setup (in a terminal): 

- Set up proper privilege to be able to run the demo:

> chmod +x ./vt_install_prereqs.sh

- Install all dependent libraries etc.(Make sure you only do this command once)

> sudo ./vt_install_prereqs.sh


II. Start VisTrails: 

- Change directory to "WorkflowRecommendation­master/vistrails" and start VisTrails:

> cd ./WorkflowRecommendation­master/vistrails

> python vistrails.py


III. Enable Plugin: 

- In VisTrails, go to "Edit ­> Preferences ­> Module Packages" and enable the following plugin:

 ­> componentGraph, components, and componentSearch packages


IV. Run our software: 

- In VisTrails, go to "Packages ­> Recommendation Engine".



## To update the pulgin

1. The main code for the component search locates at vistrails_current/vistrails/packages/componentSearch/component_search_form.py

2. Check the origin VisTrails folder from GitHub here: https://github.com/cmusv-sc/VisTrailsRecommendation

3. All the recommendation APIs used is here from Github: https://github.com/cmusv-sc/RecommendationAPIs




