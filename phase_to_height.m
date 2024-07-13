function [height_map, point_cloud] = phase_to_height(data, distance_reference_plane, distance_CCD_projector, period)
    % Unwrap the phase using Goldstein's algorithm
    unwrapped_phase_map = takeda_phase_unwrap(data);

    % Convert unwrapped phase to height distributionñ
    height_map = (unwrapped_phase_map * period) / (2*pi);

    % Convert height to real-world coordinates (in meters)
    height_map = (height_map * distance_reference_plane) /(distance_CCD_projector);

    % Reconstruct the 3D object
    [rows, cols] = size(height_map);
    [X, Y] = meshgrid(1:cols, 1:rows);
    X = X - (cols + 1) / 2; % Centering X and Y coordinates
    Y = Y - (rows + 1) / 2;
    point_cloud = [X(:), Y(:), height_map(:)];
end


% Example usage:
% Load your wrapped phase map (replace 'wrapped_phase_map' with your data)
% load('wrapped_phase_map.mat'); % Assuming the data is stored in 'wrapped_phase_map' variable

