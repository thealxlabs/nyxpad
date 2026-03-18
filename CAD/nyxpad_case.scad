$fn=64;
WALL=2.5; FLOOR=2.0; TOP_T=3.0; INNER_H=12.5;
PCB_W=80; PCB_D=70; CR=3.5;
KEY_HOLE=14.0; OLED_W=30.0; OLED_H=13.0;
ENC_D=7.5; USB_W=11.0; USB_H=5.0;
SO_H=3.5; SO_OD=5.5; SC=2.7;
SNAP_H=1.2; SNAP_W=1.0;

module rbox(w,d,h,r=CR){
  hull()for(x=[r,w-r],y=[r,d-r])translate([x,y,0])cylinder(r=r,h=h);
}

module standoff(x,y){
  translate([x+WALL,y+WALL,FLOOR])
    difference(){
      cylinder(d=SO_OD,h=SO_H);
      cylinder(d=SC,h=SO_H+0.1);
    }
}

module nyxpad_bottom(){
  difference(){
    rbox(PCB_W+WALL*2,PCB_D+WALL*2,FLOOR+INNER_H);
    translate([WALL,WALL,FLOOR])rbox(PCB_W,PCB_D,INNER_H+0.1,CR-1);
    translate([WALL+22-USB_W/2,PCB_D+WALL*2-0.1,FLOOR+INNER_H-USB_H-1])
      cube([USB_W,WALL+0.2,USB_H+1]);
    translate([WALL-SNAP_W,WALL,FLOOR+INNER_H-SNAP_H-0.5])cube([SNAP_W+0.1,PCB_D,SNAP_H]);
    translate([PCB_W+WALL,WALL,FLOOR+INNER_H-SNAP_H-0.5])cube([SNAP_W+0.1,PCB_D,SNAP_H]);
    translate([WALL,WALL-SNAP_W,FLOOR+INNER_H-SNAP_H-0.5])cube([PCB_W,SNAP_W+0.1,SNAP_H]);
    translate([WALL,PCB_D+WALL,FLOOR+INNER_H-SNAP_H-0.5])cube([PCB_W,SNAP_W+0.1,SNAP_H]);
  }
  standoff(4,4);
  standoff(PCB_W-4-SO_OD/2,4);
  standoff(4,PCB_D-4-SO_OD/2);
  standoff(PCB_W-4-SO_OD/2,PCB_D-4-SO_OD/2);
}

module nyxpad_top(){
  difference(){
    union(){
      rbox(PCB_W+WALL*2,PCB_D+WALL*2,TOP_T);
      translate([WALL,WALL,-SNAP_H])cube([SNAP_W,PCB_D,SNAP_H]);
      translate([PCB_W+WALL,WALL,-SNAP_H])cube([SNAP_W,PCB_D,SNAP_H]);
      translate([WALL,WALL,-SNAP_H])cube([PCB_W,SNAP_W,SNAP_H]);
      translate([WALL,PCB_D+WALL,-SNAP_H])cube([PCB_W,SNAP_W,SNAP_H]);
    }
    for(kx=[14,33.05,52.1],ky=[38,57.05])
      translate([WALL+kx-KEY_HOLE/2,WALL+ky-KEY_HOLE/2,-0.1])
        cube([KEY_HOLE,KEY_HOLE,TOP_T+0.2]);
    translate([WALL+62-OLED_W/2,WALL+8-OLED_H/2,-0.1])
      cube([OLED_W,OLED_H,TOP_T+0.2]);
    translate([WALL+63,WALL+47,-0.1])cylinder(d=ENC_D,h=TOP_T+0.2);
    for(x=[WALL+4,WALL+PCB_W-4],y=[WALL+4,WALL+PCB_D-4])
      translate([x,y,-0.1])cylinder(d=SC,h=TOP_T+0.2);
    translate([WALL+8,WALL+PCB_D-8,TOP_T-0.5])
      linear_extrude(0.6)
        text("NYX PAD",size=3.5,font="Liberation Sans:style=Bold",halign="left");
  }
}

// To export Top.stl:    comment out nyxpad_bottom(), keep nyxpad_top()
// To export Bottom.stl: comment out nyxpad_top(),   keep nyxpad_bottom()
//nyxpad_bottom();
//translate([PCB_W+WALL*2+15,0,0]) nyxpad_top();
