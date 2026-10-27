extends Node

# Temporary tool for the press kit logo. Renders a lit penguin headshot on a transparent background
# and saves it to the path passed after "--". Passing "clean" after the path leaves out the blood.

const PENGUIN_SCENE: PackedScene = preload("res://prefabs/penguin.tscn")
const SETTLE_FRAMES: int = 30

func _ready() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var output_path: String = arguments[0]
	var clean: bool = arguments.size() > 1 and arguments[1] == "clean"
	get_node(^"/root/FpsCounter").queue_free()
	get_viewport().transparent_bg = true

	var environment: Environment = Environment.new()
	environment.background_mode = Environment.BG_CLEAR_COLOR
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.55, 0.6, 0.75)
	environment.ambient_light_energy = 0.6
	var world_environment: WorldEnvironment = WorldEnvironment.new()
	world_environment.environment = environment
	add_child(world_environment)

	add_light(Vector3(2, 3, 3), 1.6, Color(1.0, 0.95, 0.9))
	add_light(Vector3(-3, 1, 1), 0.5, Color(0.6, 0.7, 1.0))
	add_light(Vector3(0, 2, -3), 1.2, Color(1.0, 0.4, 0.4))

	var penguin: Penguin = PENGUIN_SCENE.instantiate()
	add_child(penguin)
	penguin.set_color(Color("e6194b"))
	penguin.set_pattern("skulls")
	# Both eyes have to be open and looking out over the lettering.
	penguin.blink_timer.stop()
	if not clean:
		penguin.set_blood_amount(1.0)
		# Far more than the game ever shows, so the logo reads as bloody even when small.
		penguin.blood_material.set_shader_parameter(&"coverage", 0.55)

	for frame in SETTLE_FRAMES:
		await get_tree().process_frame
	var head: Vector3 = penguin.head.global_position
	var camera: Camera3D = Camera3D.new()
	camera.fov = 30.0
	add_child(camera)
	camera.global_position = head + Vector3(0, 0.12, 1.5)
	camera.look_at(head + Vector3(0, 0.02, 0))
	camera.make_current()
	for frame in SETTLE_FRAMES:
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(output_path)
	get_tree().quit()

func add_light(direction: Vector3, energy: float, color: Color) -> void:
	var light: DirectionalLight3D = DirectionalLight3D.new()
	light.light_energy = energy
	light.light_color = color
	add_child(light)
	light.look_at_from_position(direction, Vector3.ZERO)
