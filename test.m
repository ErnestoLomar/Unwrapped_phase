% Define parameters
tic
distance_reference_plane = 120; % m
distance_CCD_projector = 10; % cm
period = 100; % Fringe period (in arbitrary units, could be pixels)

%Unwapping phase using Goldstein algorithm

fase_desenvuelta=goldstein_unwrapp(d_phi2);

% Perform phase-to-height conversion and get the point cloud
[height_map, point_cloud] = phase_to_height(fase_desenvuelta, distance_reference_plane, distance_CCD_projector, period);

% Display the height map and point cloud (assuming you have the 'pcshow' function available)
figure;
subplot(1, 2, 1);
imshow(height_map, []);
title('Height Map');

subplot(1, 2, 2);
pcshow(point_cloud,point_cloud(:, 3));
colormap(gray)
title('Point Cloud');


writematrix(fase_desenvuelta, 'desenvuelta_gol2_50');
writematrix(fase_desenvuelta, 'desenvuelta_gol2_50.csv');

writematrix(height_map, 'alturas_gol2_50');
writematrix(height_map, 'alturas_gol2_50.csv');

writematrix(point_cloud, 'nube_gol2_50');
writematrix(point_cloud, 'nube_gol2_50.csv');
toc
