Adapted from https://www.pyimagesearch.com/2018/09/24/opencv-face-recognition/

#Setup
    sudo apt install python3-pip
    python3 -m pip install --upgrade imutils
    python3 -m pip install --upgrade pip
    python3 -m pip install scikit-learn
    python3 -m pip install --upgrade protobuf
    python3 -m pip uninstall numpy
    python3 -m pip install numpy==1.16.4

#Usage

To add a person to the dataset, make a directory in `dataset/` with the name of the person, then populate the directory with at least 10 images of that person.

Extract embeddings from the faces in the dataset:

    python3 extract_embeddings.py --dataset dataset --embeddings output/embeddings.pickle --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7

Train the model:

    python3 train_model.py --embeddings output/embeddings.pickle --recognizer output/recognizer.pickle --le output/le.pickle

To recognize faces in an *image*:

    python3 recognize.py --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7 --recognizer output/recognizer.pickle --le output/le.pickle --image <IMAGE>

To recognize faces in a *video stream*:

    python3 recognize_video.py --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7 --recognizer output/recognizer.pickle --le output/le.pickle
