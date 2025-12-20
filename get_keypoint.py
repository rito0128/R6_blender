import bpy
from bpy_extras.object_utils import world_to_camera_view

# --- 設定 ---
# 4台のカメラの名称リスト
# シーン内の実際のカメラ名に合わせて変更してください。
CAMERA_NAMES = ["Camera.001", "Camera.002", "Camera.003", "Camera.004"]

# 出力ディレクトリのパス (Blenderの実行環境に合わせて絶対パスを指定)
# 例: "/tmp/renders/" または "C:/Users/YourName/Desktop/renders/"
OUTPUT_DIR = "C:/Users/sinki/R6_blender/img/" # "//" はBlenderファイルからの相対パスを意味します。

# レンダリング画像の設定
IMAGE_FORMAT = 'PNG'
RESOLUTION_X = 1920
RESOLUTION_Y = 1080
# --------------------

def setup_render_settings(scene, output_dir, format):
    """シーンのレンダリング基本設定を行う"""
    scene.render.image_settings.file_format = format
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.filepath = output_dir # 出力パスの基本設定

def render_from_multiple_cameras(ARMATURE_NAME):
    """複数のカメラから順番にレンダリングを実行するメイン関数"""
    scene = bpy.context.scene
    
    # 1. 基本設定の適用
    setup_render_settings(scene, OUTPUT_DIR, IMAGE_FORMAT)
    
    # 2. カメラリストを反復処理
    for i, camera_name in enumerate(CAMERA_NAMES):
        camera = bpy.data.objects.get(camera_name)
        
        if camera and camera.type == 'CAMERA':
            print(f"--- レンダリング開始: {camera_name} ({i + 1}/{len(CAMERA_NAMES)}) ---")
            
            # **現在のカメラをアクティブなシーンカメラとして設定**
            scene.camera = camera
            
            get_bone_pixel_coords(scene, camera, ARMATURE_NAME)
            
            # **出力ファイル名をカメラごとに設定**
            # 例: //renders/output_Camera.001
            scene.render.filepath = f"{OUTPUT_DIR}output_{camera_name}"
            
            # **レンダリングの実行**
            # write_still=True: レンダリングが完了した後、ファイルに画像を保存します。
            bpy.ops.render.render(write_still=True)
            
            print(f"レンダリング完了。出力: {scene.render.filepath}")
        else:
            print(f"警告: カメラ '{camera_name}' が見つからないか、カメラオブジェクトではありません。スキップします。")

# def get_bone_world_coords(armature_name):
#     # アーマチュアオブジェクトを取得
#     obj = bpy.data.objects.get(armature_name)
    
#     if not obj or obj.type != 'ARMATURE':
#         print(f"❌ エラー: '{armature_name}' という名前のアーマチュアが見つかりません。")
#         return

#     # アーマチュアのワールド行列を取得（オブジェクト自体の移動・回転・スケール）
#     matrix_world = obj.matrix_world

#     print(f"--- Armature: {armature_name} (World Coordinates) ---")

#     # ポーズボーン（ポーズ適用後の状態）をループ処理
#     for pbone in obj.pose.bones:
#         # pbone.head / pbone.tail はアーマチュア空間（ローカル）の座標
#         # これに matrix_world を掛けてワールド座標に変換
#         head_world = matrix_world @ pbone.head
#         tail_world = matrix_world @ pbone.tail

#         print(f"Bone: {pbone.name}")
#         print(f"  Head: ({head_world.x:.4f}, {head_world.y:.4f}, {head_world.z:.4f})")
#         print(f"  Tail: ({tail_world.x:.4f}, {tail_world.y:.4f}, {tail_world.z:.4f})")

def get_bone_pixel_coords(scene, camera, armature_name):
    """ボーンのワールド座標を画像平面のピクセル座標に変換して表示する"""
    obj = bpy.data.objects.get(armature_name)
    if not obj or obj.type != 'ARMATURE':
        print(f"❌ アーマチュア '{armature_name}' が見つかりません。")
        return

    matrix_world = obj.matrix_world
    print(f"\n[Camera: {camera.name}] Bone 2D Coordinates (Pixel):")

    for pbone in obj.pose.bones:
        # 1. ワールド座標を計算
        head_world = matrix_world @ pbone.head
        tail_world = matrix_world @ pbone.tail

        # 2. 3Dワールド座標をカメラビューの2D比率(0.0 - 1.0)に変換
        # 返り値は Vector((x, y, z))。zはカメラからの深度（正ならカメラの前方）
        head_view = world_to_camera_view(scene, camera, head_world)
        tail_view = world_to_camera_view(scene, camera, tail_world)

        # 3. 比率をピクセル座標に変換
        # Blenderの画像座標系は左下が(0,0)のため、必要に応じて上下反転の処理を行う
        head_px = (head_view.x * RESOLUTION_X, (1.0 - head_view.y) * RESOLUTION_Y)
        tail_px = (tail_view.x * RESOLUTION_X, (1.0 - tail_view.y) * RESOLUTION_Y)

        # カメラの画角内（0.0~1.0の範囲内）にあるかチェック
        in_view = "In Frame" if (0 <= head_view.x <= 1 and 0 <= head_view.y <= 1) else "Out of Frame"

        print(f"Bone: {pbone.name} ({in_view})")
        print(f"  Head: X={head_px[0]:.2f}, Y={head_px[1]:.2f} (z_depth={head_view.z:.2f})")
        print(f"  Tail: X={tail_px[0]:.2f}, Y={tail_px[1]:.2f} (z_depth={tail_view.z:.2f})")

# 実行（アーマチュア名を指定してください）
render_from_multiple_cameras("Armature")