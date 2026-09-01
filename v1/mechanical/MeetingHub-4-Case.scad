// MeetingHub-4 - Enclosure (OpenSCAD)
// Version: 0.1 (DRAFT - not yet visually verified, see mechanical/README.md)
//
// Coordinate convention matches the PCB's own reference frame from
// PCB-001-LayoutGuide.md Fase 4/5: Y=0 is the BACK of the device
// (J1/J2-J5 side), Y=pcb_h is the FRONT (J6/SW1-5 side), Z is UP
// (RV1-5 potentiometer shafts point up through the lid).
//
// All component positions below are copied directly from the real,
// DRC-clean MeetingHub-4.kicad_pcb (checked via pcbnew), relative to
// the board's own bottom-left corner (0,0). Component HEIGHTS
// (relay, electrolytic caps, pot shaft length, DIP-8 socket) are NOT
// in any project file - the values below are typical/approximate for
// these part families and are called out explicitly. Verify against
// the real datasheets/parts before printing, and adjust `wall_height`
// and `shaft_reach` if needed.

// ---------- Board facts (from MeetingHub-4.kicad_pcb) ----------
pcb_w = 265.1;
pcb_h = 160.1;
pcb_t = 1.6;

// Mounting holes (M3, unplated 3.2mm), relative to board corner
mh_positions = [[6.05,6.05], [259.05,6.05], [6.05,154.05], [259.05,154.05]];
mh_drill = 3.2;

// Back panel (Y=0 side): J1 (USB-C) + J2-J5 (TRRS to notebooks)
usb_c_pos = [210.05, 15.05];
trrs_back_pos = [[50.05,15.05], [90.05,15.05], [130.05,15.05], [170.05,15.05]]; // J2..J5

// Front panel (Y=pcb_h side): J6 (headset TRRS) + SW1-5 anchor points
trrs_front_pos = [170.05, 147.05]; // J6
sw_anchor_pos = [[80.05,147.05],[98.05,147.05],[116.05,147.05],[134.05,147.05],[152.05,147.05]]; // SW1..SW5

// Top panel: RV1-5 potentiometer shafts (assumed to point +Z, per
// PCB-001 Fase 3.1: "eixo do RK097 aponta pra cima")
rv_positions = [[50.05,85.05],[90.05,85.05],[130.05,85.05],[170.05,85.05],[210.05,85.05]]; // RV1..RV5

// ---------- Enclosure parameters (assumptions - adjust freely) ----------
wall = 2.5;             // wall thickness, typical for FDM
margin = 5;             // clearance from PCB edge to inner wall (X and Y)
standoff_h = 5;         // PCB stands this high above the case floor
// ASSUMPTION: tallest components above the PCB top surface (relay
// G5V-1 ~15.7mm, DIP-8 + socket ~10mm, 220uF radial cap ~16mm, RK097
// pot body ~10mm) - not from a project file, typical datasheet values.
component_clearance = 20;
wall_height = standoff_h + pcb_t + component_clearance; // inner cavity height
lid_t = 2.5;

// Cutout sizes (generous "clearance window" style rather than tight
// datasheet-precision cutouts, since exact connector protrusion depth
// isn't documented - see mechanical/README.md before finalizing)
trrs_cut_w = 10;   // 3.5mm TRRS jack window
trrs_cut_h = 9;
usb_cut_w = 11;    // USB-C window
usb_cut_h = 6;
pot_hole_d = 7;    // RK097 shaft/bushing clearance hole
sw_hole_d = 7;     // generic mini toggle/pushbutton hole - resize to your actual switch

// Corner standoffs for the lid screws (separate from the PCB's own
// mounting posts), inset from the OUTER case corner
lid_post_inset = 6;
lid_post_od = 8;
lid_screw_d = 3.2;

// ---------- Derived ----------
case_w = pcb_w + 2*margin + 2*wall;
case_h = pcb_h + 2*margin + 2*wall;
pcb_origin = [wall+margin, wall+margin]; // PCB (0,0) in case-local XY

module mounting_post(d_outer, d_hole, h) {
    difference() {
        cylinder(d=d_outer, h=h, $fn=32);
        translate([0,0,-1]) cylinder(d=d_hole, h=h+2, $fn=24);
    }
}

module bottom_shell() {
    difference() {
        union() {
            // floor + walls
            cube([case_w, case_h, wall]);
            difference() {
                cube([case_w, case_h, wall_height]);
                translate([wall, wall, wall])
                    cube([case_w-2*wall, case_h-2*wall, wall_height]);
            }
        }
        // Back panel cutouts (Y=0 side): J1 + J2-J5
        translate([pcb_origin[0]+usb_c_pos[0], -1, wall+standoff_h+pcb_t-usb_cut_h/2])
            cube([usb_cut_w, wall+2, usb_cut_h]);
        for (p = trrs_back_pos)
            translate([pcb_origin[0]+p[0]-trrs_cut_w/2, -1, wall+standoff_h+pcb_t-trrs_cut_h/2])
                cube([trrs_cut_w, wall+2, trrs_cut_h]);

        // Front panel cutouts (Y=pcb_h side): J6 + SW1-5
        translate([pcb_origin[0]+trrs_front_pos[0]-trrs_cut_w/2, case_h-wall-1, wall+standoff_h+pcb_t-trrs_cut_h/2])
            cube([trrs_cut_w, wall+2, trrs_cut_h]);
        for (p = sw_anchor_pos)
            translate([pcb_origin[0]+p[0], case_h-wall-1, wall+standoff_h+pcb_t+8])
                rotate([-90,0,0]) cylinder(d=sw_hole_d, h=wall+2, $fn=24);
    }

    // PCB mounting standoffs (M3), positioned at MH1-4
    for (p = mh_positions)
        translate([pcb_origin[0]+p[0], pcb_origin[1]+p[1], wall])
            mounting_post(d_outer=7, d_hole=mh_drill, h=standoff_h);

    // Lid screw standoffs, near the 4 outer corners
    lid_post_xy = [
        [lid_post_inset, lid_post_inset],
        [case_w-lid_post_inset, lid_post_inset],
        [lid_post_inset, case_h-lid_post_inset],
        [case_w-lid_post_inset, case_h-lid_post_inset]
    ];
    for (p = lid_post_xy)
        translate([p[0], p[1], wall])
            mounting_post(d_outer=lid_post_od, d_hole=lid_screw_d*0.85, h=wall_height-wall); // self-tap pilot hole
}

module lid() {
    difference() {
        cube([case_w, case_h, lid_t]);
        // pot shaft holes
        for (p = rv_positions)
            translate([pcb_origin[0]+p[0], pcb_origin[1]+p[1], -1])
                cylinder(d=pot_hole_d, h=lid_t+2, $fn=24);
        // lid screw clearance holes (through-holes, no threads)
        lid_post_xy = [
            [lid_post_inset, lid_post_inset],
            [case_w-lid_post_inset, lid_post_inset],
            [lid_post_inset, case_h-lid_post_inset],
            [case_w-lid_post_inset, case_h-lid_post_inset]
        ];
        for (p = lid_post_xy)
            translate([p[0], p[1], -1])
                cylinder(d=lid_screw_d, h=lid_t+2, $fn=24);
    }
}

// ---------- Render ----------
// Comment one out / translate the other sideways to view both at once
bottom_shell();
translate([case_w + 20, 0, 0]) lid();
