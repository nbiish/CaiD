import bpy
import bmesh
import os

def create_laser_stand():
    # Parameters
    SLOT_WIDTH = 6.43 + 0.4  # 6.63mm
    ARM_LENGTH = 45.0        # Length of each arm of the L
    STAND_HEIGHT = 45.0      # Total height
    WALL_THICKNESS = 4.0     # Wall thickness
    SLOT_DEPTH_FROM_TOP = 20.0 # How deep the plate sits into the stand
    
    # Derived params
    # The stand needs to be wider than the slot
    # Total Width of the arm profile = Wall + Slot + Wall? 
    # Or does it sit under?
    # Let's assume the stand is a solid L-block with a slot in the top face.
    BLOCK_WIDTH = SLOT_WIDTH + (WALL_THICKNESS * 2)
    
    # Clear existing
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Helper to make a cube (center based)
    def make_cube(name, size, loc):
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = size
        obj.location = loc
        bpy.ops.object.transform_apply(scale=True, location=False)
        return obj

    # 1. Create L-Shaped Body
    # Arm 1 (X-axis)
    # Size: (ARM_LENGTH, BLOCK_WIDTH, STAND_HEIGHT)
    # Pos: (ARM_LENGTH/2 - BLOCK_WIDTH/2, 0, STAND_HEIGHT/2) -> corner at 0,0?
    # Let's place the inner corner at 0,0
    
    # Inner corner at 0,0 means:
    # Arm X stretches from X=0 to X=ARM_LENGTH
    # Arm Y stretches from Y=0 to Y=ARM_LENGTH
    # But they overlap at the corner.
    
    # Re-think origin: Let 0,0,Z be the corner of the PLATE.
    # The stand should wrap around this.
    
    # Body Arm X
    body_x = make_cube("Body_X", 
                       (ARM_LENGTH, BLOCK_WIDTH, STAND_HEIGHT), 
                       (ARM_LENGTH/2 - WALL_THICKNESS, -BLOCK_WIDTH/2 + WALL_THICKNESS, STAND_HEIGHT/2))
                       
    # Body Arm Y
    body_y = make_cube("Body_Y", 
                       (BLOCK_WIDTH, ARM_LENGTH, STAND_HEIGHT), 
                       (-BLOCK_WIDTH/2 + WALL_THICKNESS, ARM_LENGTH/2 - WALL_THICKNESS, STAND_HEIGHT/2))
    
    # Join Body
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = body_x
    body_x.select_set(True)
    body_y.select_set(True)
    try:
        bpy.ops.object.join()
    except Exception as e:
        print(f"Body Join failed: {e}")
        
    body = body_x
    body.name = "Stand_Body"

    # 2. Create L-Shaped Slot Cutter
    # This represents the plate fitting into the stand.
    # Plate corner is at 0,0.
    # Plate thickness = SLOT_WIDTH.
    # Does the plate sit vertically or horizontally?
    # "bed plate" usually horizontal.
    # So slot should be Horizontal cut?
    # "Fit over the metal plate stand... 6.43 thick".
    # "Slip ... onto and holding the bed plate".
    # Implies a horizontal interaction if it's a bed?
    # NO, usually "stand" means vertical leg.
    # If the "metal plate stand" is 6.43mm thick, maybe it's a vertical sheet metal leg?
    # BUT "holding the bed plate".
    
    # LET'S ASSUME STANDARD CORNNER BRACKET: Vertical Leg holding a horizontal bed?
    # OR: The Printed Part IS the Leg. It grabs the Horizontal Bed Plate.
    # So the Slot matches the Bed Plate (Horizontal).
    
    # Slot Dimensions:
    # Thickness (Z) = SLOT_WIDTH? NO, plates usually flat (XY). So thickness is Z.
    # So we need a horizontal slot of height 6.43mm.
    
    # Wait, existing prompt: "thickness of the sections... 6.43 thick".
    # "stand is a metal plate that will slip into the 6 point43 Section".
    # "slip each of these onto... the bed plate".
    
    # Let's make a VERTICAL SLOT if it slips onto a "metal plate stand" (leg).
    # Let's make a HORIZONTAL SLOT if it slips onto a "bed plate".
    # COMPROMISE: The sketch showed a vertical thing.
    # BUT "Slip...onto... bed plate".
    # I will stick to my previous Logic: A vertical Slot? 
    # My previous code made a vertical slot (Cutout scaled to fit vertical plate).
    # User approved "LGTM" on the plan which had "Vertical block slips over plate".
    
    # WAIT! "The stand is a metal plate... slip into the 6.43 section".
    # THIS TIME: L-SHAPED CORNER.
    # A corner of a horizontal bed? That implies horizontal slot.
    # A corner of a vertical angle iron leg? That implies vertical slot (L-profile).
    
    # DECISION: VERTICAL L-PROFILE SLOT (Angle Iron shape).
    # Why? "metal plate stand" (singular vertical stand?).
    # And "fit over the metal plate stand".
    # Fits over a vertical angle iron.
    
    # Cutter Arm X
    # Thickness = SLOT_WIDTH
    # Depth/Height = TALL (to cut through top or bottom)
    # Length = ARM_LENGTH + buffer
    
    cutter_x = make_cube("Cut_X",
                         (ARM_LENGTH + 10, SLOT_WIDTH, STAND_HEIGHT * 2),
                         ((ARM_LENGTH+10)/2 - WALL_THICKNESS, -SLOT_WIDTH/2 + WALL_THICKNESS, STAND_HEIGHT))
                         
    cutter_y = make_cube("Cut_Y",
                         (SLOT_WIDTH, ARM_LENGTH + 10, STAND_HEIGHT * 2),
                         (-SLOT_WIDTH/2 + WALL_THICKNESS, (ARM_LENGTH+10)/2 - WALL_THICKNESS, STAND_HEIGHT))
                         
    # Join Cutters
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = cutter_x
    cutter_x.select_set(True)
    cutter_y.select_set(True)
    try:
        bpy.ops.object.join()
    except Exception as e:
        print(f"Cutter Join failed: {e}")
        
    cutter = cutter_x
    cutter.name = "Slot_Cutter"
    
    # Move Cutter DOWN to leave a "roof" or UP to leave a "floor"?
    # If it's a foot, it needs a floor (bottom solid).
    # If it's a cap, it needs a roof.
    # "Hold up... bed". So this is a foot. It sits on floor, plate sits inside it.
    # So we need a BOTTOM SOLID LAYER.
    BOTTOM_THICKNESS = 5.0
    cutter.location.z = (STAND_HEIGHT / 2) + BOTTOM_THICKNESS
    
    # Boolean Difference
    mod = body.modifiers.new(name="SlotCut", type='BOOLEAN')
    mod.object = cutter
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="SlotCut")
    
    # Cleanup
    bpy.data.objects.remove(cutter, do_unlink=True)
    
    # 3. Add Bevels for Aesthetics and Fit
    # Bevel all edges slightly
    bevel = body.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 1.0  # 1mm bevel
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = 0.523599 # 30 degrees
    # Apply Bevel? Or leave it for export?
    # Better to apply for STL export if we want the geometry baked.
    bpy.ops.object.modifier_apply(modifier="Bevel")
    
    return body

create_laser_stand()
