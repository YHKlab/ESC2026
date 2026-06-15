#gnuplot
set terminal pngcairo size 1920,1080 font 'Arial,20' linewidth 2
set output 'pbe.png'

#set label
set style fill solid 1.0 border lc rgb "black"
set key opaque
set key box lw 1 lc rgb "black"
set key font 'Arial,24'           # font/size
set key textcolor rgb "black"  

E_f =0
E_f1 = 6.2275

ymin = -14 #-E_f1 
ymax = 8 #-E_f1
L = 0.0
G1 = 0.6124
X = 1.3195
U = 1.5695
G2 = 2.3195

set yrange[(E_f+ymin):(E_f+ymax)]
set xrange[0:G2]

set arrow from  L,  ymin+E_f to  L, ymax+E_f nohead
set arrow from  G1,  ymin+E_f to  G1, ymax+E_f nohead
set arrow from  X,  ymin+E_f to  X, ymax+E_f nohead
set arrow from  U,  ymin+E_f to  U, ymax+E_f nohead
set arrow from  G2,  ymin+E_f to  G2, ymax+E_f nohead
set xtics ("L" 0, "G" G1, "X" X, "U|K" U, "G" G2) 
plot "pp.out.gnu" u 1:($2-E_f1) w l lw 2 lt 1 lc rgb "black" title '  PBE' 

#pause -1
