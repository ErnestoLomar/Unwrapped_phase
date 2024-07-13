function unwrapped_phase = takeda_phase_unwrap(wrapped_phase)
    % wrapped_phase: 2D array containing the wrapped phase

    % Calculate gradient of the wrapped phase
    [gx, gy] = gradient(wrapped_phase);

    % Compute the Laplacian of the gradient
    laplacian = del2(gx + 1i * gy);

    % Compute the 2D unwrapped phase using Fourier transform
    unwrapped_phase = real(ifft2(-laplacian));

    % Adjust the phase to be in the range [-pi, pi]
    unwrapped_phase = mod(unwrapped_phase + pi, 2 * pi) - pi;
end
