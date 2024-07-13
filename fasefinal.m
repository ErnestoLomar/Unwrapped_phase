
%Lectura de las Imagenes
R1=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\ref1.JPG'));
R2=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\ref2.JPG'));
R3=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\ref3.JPG'));
R4=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\ref4.JPG'));
%R5=double(imread('C:\users\NOGARD\Documents\MATLAB\Franjas\imagenes\capture2\5\R5.bmp'));
D1=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\def1.JPG'));
D2=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\def2.JPG'));
D3=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\def3.JPG'));
D4=double(imread('C:\Users\nogard\Dropbox\franjas\Curso Maestria IF\Einstein\periodo_100\def4.JPG'));
%D5=double(imread('C:\users\NOGARD\Documents\MATLAB\Franjas\imagenes\capture2\5\D5.bmp'));

NR=R2-R4;
DR=R1-R3;
ND=D2-D4;
DD=D1-D3;

d_phi=atan2(((ND.*DR)-(NR.*DD)),((DD.*DR)+(ND.*NR)));
d_phi2=d_phi(:,:,1);
% for i=1:size(d_phi,1)
%     for j=1:size(d_phi,2)
%         if d_phi2(i,j)<-0.8*pi
%             d_phi2(i,j)=d_phi2(i,j)+2*pi;
%         end
%     end
% end
%d_phi(d_phi<-pi)=d_phi(d_phi<-pi)+pi;
figure
fase100=imagesc(d_phi2);
colormap(gray);
save('fase_100.mat', 'd_phi2')

% salida=writematrix(fase10);
% type 'fase10.m'

