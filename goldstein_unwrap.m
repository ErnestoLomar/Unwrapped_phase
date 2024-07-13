function unwrapped_phase = goldstein_unwrap(phase_map)
    [rows, cols] = size(phase_map);

    % Initialize the unwrapped phase map
    unwrapped_phase = zeros(rows, cols);

    % Phase difference thresholds
    threshold = pi;

    % Loop through each pixel in the phase map
    for r = 1:rows
        for c = 1:cols
            % Calculate differences between neighboring pixels
            delta_r = 0;
            delta_c = 0;
            for dr = -1:1
                for dc = -1:1
                    if dr ~= 0 || dc ~= 0
                        r_neighbor = r + dr;
                        c_neighbor = c + dc;
                        if r_neighbor >= 1 && r_neighbor <= rows && c_neighbor >= 1 && c_neighbor <= cols
                            delta_r = delta_r + sin(phase_map(r_neighbor, c_neighbor) - phase_map(r, c));
                            delta_c = delta_c + cos(phase_map(r_neighbor, c_neighbor) - phase_map(r, c));
                        end
                    end
                end
            end

            % Calculate the unwrapped phase value
            unwrapped_phase(r, c) = phase_map(r, c) + atan2(delta_r, delta_c);

            % Perform 2π jumps corrections
            while (unwrapped_phase(r, c) - phase_map(r, c)) > threshold
                unwrapped_phase(r, c) = unwrapped_phase(r, c) - 2*pi;
            end

            while (unwrapped_phase(r, c) - phase_map(r, c)) < -threshold
                unwrapped_phase(r, c) = unwrapped_phase(r, c) + 2*pi;
            end
        end
    end
end
