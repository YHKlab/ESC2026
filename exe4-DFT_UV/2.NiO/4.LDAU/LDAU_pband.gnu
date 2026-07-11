#gnuplot
set terminal pngcairo size 1920,1080 font "Arial,20" linewidth 2
set output 'ldaU.png'

#set label
set style fill solid 1.0 border lc rgb "black"
set key opaque
set key box lw 1 lc rgb "black"
set key font "Arial,24"           # font/size
set key textcolor rgb "black"  

E_f =0
E_f1 = 13.7999

ymin = -8 #-E_f1 
ymax = 8 #-E_f1
G1 = 0
L = 1.0050
B = 1.6493
Z1 = 2.7185
G2 = 3.2496
X = 4.4285
F = 4.9631
P1 = 5.1511
Z2 = 6.0771

set yrange[(E_f+ymin):(E_f+ymax)]
set xrange[0:G2]

set arrow from  L,  ymin+E_f to  L, ymax+E_f nohead
set arrow from  B,  ymin+E_f to  B, ymax+E_f nohead
set arrow from  Z1,  ymin+E_f to  Z1, ymax+E_f nohead
set arrow from  G2,  ymin+E_f to  G2, ymax+E_f nohead
#set arrow from  X,  ymin+E_f to  X, ymax+E_f nohead
#set arrow from  F,  ymin+E_f to  F, ymax+E_f nohead
#set arrow from  P1,  ymin+E_f to  P1, ymax+E_f nohead
set xtics ("G" G1,"L" L,"B1|B" B,"Z" Z1, "G" G2) #, "X|Q" X, "F" F,"P1" P1, "Z" Z2) 
plot "pp.out.gnu" u 1:($2-E_f1) w l lw 2 lt 1 lc rgb "black" title '  LDA+U' 

#pause -1
