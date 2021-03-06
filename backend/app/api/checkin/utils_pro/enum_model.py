model_path = 'model_data/merged_model_v1.0.h5'
anchors_path = 'model_data/drone_anchors.txt'
classes_path = 'model_data/one_class.txt'
classification_model_path = 'model_data/drone_bird_classification_model_v1.0.h5'
pre_score = 0.8
mid_score = 0.8
next_score = 0.8
big_score = 0.5
iou = 0.1
model_image_size = (1120, 1120)
gpu_num = 1

bird_label = 0
drone_label = 1
flying_label = 2
reference_fps = 25
area_threshold = 0.0001593458  # corresponds to 100 for solution 572 x 768
drone_speed_threshold = 0.006510416  # corresponds to 5 for image width 768
bird_speed_threshold = 0.015625  # corresponds to 12 for image width 768
# appear_threshold = 0.7
bbox_matching_threshold = 0.5
compute_camera_velocity = False
