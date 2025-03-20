NetTracer3D is a python package developed for both 2D and 3D analysis of microscopic images in the .tif file format. It supports generation of 3D networks showing the relationships between objects (or nodes) in three dimensional space, either based on their own proximity or connectivity via connecting objects such as nerves or blood vessels. In addition to these functionalities are several advanced 3D data processing algorithms, such as labeling of branched structures or abstraction of branched structures into networks. Note that nettracer3d uses segmented data, which can be segmented from other softwares such as ImageJ and imported into NetTracer3D, although it does offer its own segmentation via intensity and volumetric thresholding, or random forest machine learning segmentation. NetTracer3D currently has a fully functional GUI. To use the GUI, after installing the nettracer3d package via pip, enter the command 'nettracer3d' in your command prompt:


This gui is built from the PyQt6 package and therefore may not function on dockers or virtual envs that are unable to support PyQt6 displays. More advanced documentation is coming down the line, but for now please see: https://www.youtube.com/watch?v=cRatn5VTWDY
for a video tutorial on using the GUI.

NetTracer3D is free to use/fork for academic/nonprofit use so long as citation is provided, and is available for commercial use at a fee (see license file for information).

NetTracer3D was developed by Liam McLaughlin while working under Dr. Sanjay Jain at Washington University School of Medicine.

-- Version 0.6.3 updates --

1. Fixed bug with the active channel indicator on the GUI not always updating when the active channel was changed by internal loading.

2. Updated ram_lock mode in the segmenter to garbage collect better... again.

3. Added new function (Label neighborhoods). Find it in process -> image -> label neighborhoods. Allows a 3d labeled array to act as a kernel and extend its labels along a secondary binary array. This can be useful in evaluating nearest neighbors en-masse. The method behind this (smart label) was previously used internally for some methods (ie watershedding) but I thought I'd include it as an actual function since it has some more general uses.