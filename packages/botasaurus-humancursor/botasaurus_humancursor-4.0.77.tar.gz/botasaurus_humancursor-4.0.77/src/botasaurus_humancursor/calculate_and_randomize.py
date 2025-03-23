import random
import pytweening


def calculate_absolute_offset(element, relative_position, rect=None):
    """Calculates the absolute offset based on relative position"""
    if rect is None:
        # Get element position using get_bounding_rect
        rect = element.get_bounding_rect()
    
    element_width = rect["width"]
    element_height = rect["height"]
    
    x_exact_off = element_width * relative_position[0]
    y_exact_off = element_height * relative_position[1]
    
    return [int(x_exact_off), int(y_exact_off)] 


def generate_random_curve_parameters(driver, pre_origin, post_destination):
    """Generates random parameters for the curve, the tween, number of knots, distortion, target points and boundaries"""
    
    # Get window size using Botasaurus's run_js
    window_size = driver.run_js("""
        return {
            width: document.documentElement.clientWidth || window.innerWidth || document.body.clientWidth,
            height: document.documentElement.clientHeight || window.innerHeight || document.body.clientHeight
        };
    """)

    web = True
    viewport_width, viewport_height = window_size['width'],window_size['height']
    
    min_width, max_width = viewport_width * 0.15, viewport_width * 0.85
    min_height, max_height = viewport_height * 0.15, viewport_height * 0.85

    tween_options = [
        pytweening.easeOutExpo,
        pytweening.easeInOutQuint,
        pytweening.easeInOutSine,
        pytweening.easeInOutQuart,
        pytweening.easeInOutExpo,
        pytweening.easeInOutCubic,
        pytweening.easeInOutCirc,
        pytweening.linear,
        pytweening.easeOutSine,
        pytweening.easeOutQuart,
        pytweening.easeOutQuint,
        pytweening.easeOutCubic,
        pytweening.easeOutCirc,
    ]

    tween = random.choice(tween_options)
    offset_boundary_x = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    offset_boundary_y = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    knots_count = random.choices(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [0.15, 0.36, 0.17, 0.12, 0.08, 0.04, 0.03, 0.02, 0.015, 0.005],
    )[0]

    distortion_mean = random.choice(range(80, 110)) / 100
    distortion_st_dev = random.choice(range(85, 110)) / 100
    distortion_frequency = random.choice(range(25, 70)) / 100

    target_points = random.choice(
            random.choices(
                [range(35, 45), range(45, 60), range(60, 80)], [0.53, 0.32, 0.15]
            )[0]
        )
    

    if (
            min_width > pre_origin[0]
            or max_width < pre_origin[0]
            or min_height > pre_origin[1]
            or max_height < pre_origin[1]
    ):
        offset_boundary_x = 1
        offset_boundary_y = 1
        knots_count = 1
    if (
            min_width > post_destination[0]
            or max_width < post_destination[0]
            or min_height > post_destination[1]
            or max_height < post_destination[1]
    ):
        offset_boundary_x = 1
        offset_boundary_y = 1
        knots_count = 1
    return (
        offset_boundary_x,
        offset_boundary_y,
        knots_count,
        distortion_mean,
        distortion_st_dev,
        distortion_frequency,
        tween,
        target_points,
    )
