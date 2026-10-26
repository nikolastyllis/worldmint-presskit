extends Node

# Temporary tool for press kit screenshots. Loads the map without any networking, places posed
# penguins and saves a screenshot from each camera in SHOTS to the folder passed after "--".

const MAIN_SCENE: PackedScene = preload("res://scenes/main.tscn")
const PENGUIN_SCENE: PackedScene = preload("res://prefabs/penguin.tscn")
const KEPT_NODES: PackedStringArray = ["Environment", "PostProcessing", "vending_machine"]
const SETTLE_FRAMES: int = 30

var output_directory: String = ""

func _ready() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	output_directory = arguments[0]
	var shots: Array = JSON.parse_string(FileAccess.get_file_as_string(arguments[1]))

	get_node(^"/root/FpsCounter").queue_free()
	var main: Node = MAIN_SCENE.instantiate()
	for child in main.get_children():
		if not KEPT_NODES.has(String(child.name)):
			main.remove_child(child)
			child.free()
	add_child(main)

	var camera: Camera3D = Camera3D.new()
	add_child(camera)
	camera.make_current()

	for shot: Dictionary in shots:
		var penguins: Array[Node3D] = []
		for penguin_data: Dictionary in shot.get("penguins", []):
			penguins.append(spawn_penguin(penguin_data))
		for prop_data: Dictionary in shot.get("props", []):
			var prop: Node3D = load(prop_data["scene"]).instantiate()
			add_child(prop)
			prop.global_position = to_vector(prop_data["position"])
			penguins.append(prop)
		camera.fov = shot.get("fov", 75.0)
		camera.global_position = to_vector(shot["position"])
		camera.look_at(to_vector(shot["target"]))
		for frame in shot.get("frames", SETTLE_FRAMES):
			await get_tree().process_frame
		var image: Image = get_viewport().get_texture().get_image()
		image.resize(1920, 1080, Image.INTERPOLATE_LANCZOS)
		image.save_png(output_directory.path_join(shot["name"] + ".png"))
		for penguin in penguins:
			penguin.queue_free()
	get_tree().quit()

func spawn_penguin(data: Dictionary) -> Node3D:
	var penguin: Penguin = PENGUIN_SCENE.instantiate()
	add_child(penguin)
	penguin.global_position = to_vector(data["position"])
	if data.has("face"):
		var face: Vector3 = to_vector(data["face"])
		face.y = penguin.global_position.y
		# The penguin model faces positive z.
		penguin.look_at(face, Vector3.UP, true)
	penguin.set_color(Color(data.get("color", "e6194b")))
	penguin.set_pattern(data.get("pattern", "plain"))
	if data.get("snow", 0.0) > 0.0:
		penguin.set_snow_amount(data["snow"])
	if data.get("blood", 0.0) > 0.0:
		penguin.set_blood_amount(data["blood"])
	if data.get("limp", false):
		penguin.go_limp()
	return penguin

func to_vector(values: Array) -> Vector3:
	return Vector3(values[0], values[1], values[2])
