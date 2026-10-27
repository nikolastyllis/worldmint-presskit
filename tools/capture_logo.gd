extends Node

# Temporary tool for the press kit logo. Renders a lit penguin headshot on a transparent background
# and saves it to the path passed after "--". Passing "clean" after the path leaves out the blood.

const PENGUIN_SCENE: PackedScene = preload("res://prefabs/penguin.tscn")
const SETTLE_FRAMES: int = 30
## Rendered at a fixed size whatever the window, so separate renders line up pixel for pixel.
const IMAGE_SIZE: int = 2000

var stage: SubViewport

func _ready() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var output_path: String = arguments[0]
	var clean: bool = arguments.size() > 1 and arguments[1] == "clean"
	get_node(^"/root/FpsCounter").queue_free()
	stage = SubViewport.new()
	stage.size = Vector2i(IMAGE_SIZE, IMAGE_SIZE)
	stage.transparent_bg = true
	stage.own_world_3d = true
	stage.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(stage)

	var environment: Environment = Environment.new()
	environment.background_mode = Environment.BG_CLEAR_COLOR
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.55, 0.6, 0.75)
	environment.ambient_light_energy = 0.6
	var world_environment: WorldEnvironment = WorldEnvironment.new()
	world_environment.environment = environment
	stage.add_child(world_environment)

	add_light(Vector3(2, 3, 3), 1.6, Color(1.0, 0.95, 0.9))
	add_light(Vector3(-3, 1, 1), 0.5, Color(0.6, 0.7, 1.0))
	add_light(Vector3(0, 2, -3), 1.2, Color(1.0, 0.4, 0.4))

	var penguin: Penguin = PENGUIN_SCENE.instantiate()
	stage.add_child(penguin)
	# The orange of the game's interface (themes/game_theme.tres).
	penguin.set_color(Color(0.91, 0.39, 0.11))
	penguin.set_pattern("plain")
	# Both eyes have to be open and looking out over the lettering.
	penguin.blink_timer.stop()
	if not clean:
		penguin.set_blood_amount(1.0)
		# Splattered over the chest, with a fixed pattern that leaves the face clean.
		penguin.blood_material.set_shader_parameter(&"coverage", 0.45)
		penguin.blood_material.set_shader_parameter(&"seed", Vector3(11, 17, 29))

	for frame in SETTLE_FRAMES:
		await get_tree().process_frame
	var head: Vector3 = penguin.head.global_position
	var camera: Camera3D = Camera3D.new()
	camera.fov = 30.0
	stage.add_child(camera)
	camera.global_position = head + Vector3(0, 0.12, 1.5)
	camera.look_at(head + Vector3(0, 0.02, 0))
	camera.make_current()
	for frame in SETTLE_FRAMES:
		await get_tree().process_frame
	stage.get_texture().get_image().save_png(output_path)
	get_tree().quit()

func add_light(direction: Vector3, energy: float, color: Color) -> void:
	var light: DirectionalLight3D = DirectionalLight3D.new()
	light.light_energy = energy
	light.light_color = color
	stage.add_child(light)
	light.look_at_from_position(direction, Vector3.ZERO)
