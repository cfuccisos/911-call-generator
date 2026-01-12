/**
 * 911 Call Generator - Frontend JavaScript
 */

$(document).ready(function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Load available voices on page load
    loadVoices();

    // Preview button handlers
    $('#previewDispatcher').on('click', function() {
        const voiceId = $('#dispatcherVoice').val();
        if (voiceId) {
            previewVoice(voiceId, '911, what is your emergency?');
        }
    });

    $('#previewCaller').on('click', function() {
        const voiceId = $('#callerVoice').val();
        if (voiceId) {
            previewVoice(voiceId, 'Help! There has been an accident on the highway!');
        }
    });

    // Enable preview buttons when voice is selected
    $('#dispatcherVoice').on('change', function() {
        $('#previewDispatcher').prop('disabled', !$(this).val());
    });

    $('#callerVoice').on('change', function() {
        $('#previewCaller').prop('disabled', !$(this).val());
    });

    // Character counter for prompt
    $('#prompt').on('input', function() {
        const length = $(this).val().length;
        $('#charCount').text(length);

        if (length > 450) {
            $('#charCount').addClass('text-warning');
        } else {
            $('#charCount').removeClass('text-warning');
        }

        if (length >= 500) {
            $('#charCount').addClass('text-danger').removeClass('text-warning');
        } else {
            $('#charCount').removeClass('text-danger');
        }
    });

    // Form submission
    $('#generateForm').on('submit', function(e) {
        e.preventDefault();

        // Hide previous results and errors
        $('#resultsSection').addClass('d-none');
        $('#errorSection').addClass('d-none');

        // Show loading
        showLoading('Generating dialogue...');

        // Disable form
        disableForm();

        // Get form data
        const formData = {
            prompt: $('#prompt').val().trim(),
            call_duration: $('#callDuration').val(),
            emotion_level: $('#emotionLevel').val(),
            audio_format: $('#audioFormat').val(),
            diarized: $('#diarized').is(':checked') ? 'true' : 'false',
            dispatcher_voice_id: $('#dispatcherVoice').val(),
            caller_voice_id: $('#callerVoice').val()
        };

        // Update loading message after a delay
        setTimeout(function() {
            updateLoadingMessage('Creating speech audio...');
        }, 3000);

        setTimeout(function() {
            updateLoadingMessage('Processing audio...');
        }, 8000);

        // AJAX request to generate call
        $.ajax({
            url: '/generate',
            method: 'POST',
            data: formData,
            success: function(response) {
                console.log('Success:', response);
                hideLoading();
                enableForm();
                displayResults(response);
            },
            error: function(xhr) {
                console.error('Error:', xhr);
                hideLoading();
                enableForm();

                let errorMsg = 'An unexpected error occurred. Please try again.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                showError(errorMsg);
            }
        });
    });
});

/**
 * Show loading indicator with message
 */
function showLoading(message) {
    $('#loadingMessage').text(message);
    $('#loadingSection').removeClass('d-none');
}

/**
 * Update loading message
 */
function updateLoadingMessage(message) {
    $('#loadingMessage').text(message);
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    $('#loadingSection').addClass('d-none');
}

/**
 * Disable form inputs
 */
function disableForm() {
    $('#generateBtn').prop('disabled', true).html(
        '<span class="spinner-border spinner-border-sm" role="status"></span> Generating...'
    );
    $('#prompt').prop('disabled', true);
    $('#callDuration').prop('disabled', true);
    $('#emotionLevel').prop('disabled', true);
    $('#dispatcherVoice').prop('disabled', true);
    $('#callerVoice').prop('disabled', true);
    $('#audioFormat').prop('disabled', true);
    $('#diarized').prop('disabled', true);
    $('#previewDispatcher').prop('disabled', true);
    $('#previewCaller').prop('disabled', true);
}

/**
 * Enable form inputs
 */
function enableForm() {
    $('#generateBtn').prop('disabled', false).html(
        '<i class="bi bi-play-circle"></i> Generate Call'
    );
    $('#prompt').prop('disabled', false);
    $('#callDuration').prop('disabled', false);
    $('#emotionLevel').prop('disabled', false);
    $('#dispatcherVoice').prop('disabled', false);
    $('#callerVoice').prop('disabled', false);
    $('#audioFormat').prop('disabled', false);
    $('#diarized').prop('disabled', false);
    $('#previewDispatcher').prop('disabled', $('#dispatcherVoice').val() === '');
    $('#previewCaller').prop('disabled', $('#callerVoice').val() === '');
}

/**
 * Show error message
 */
function showError(message) {
    $('#errorMessage').text(message);
    $('#errorSection').removeClass('d-none');

    // Scroll to error
    $('html, body').animate({
        scrollTop: $('#errorSection').offset().top - 100
    }, 500);
}

/**
 * Display results after successful generation
 */
function displayResults(response) {
    console.log('Displaying results:', response);

    // Set audio source
    const audioPlayer = $('#audioPlayer')[0];
    audioPlayer.src = response.audio_url;

    // Set call details
    $('#callDuration').text(formatDuration(response.duration));
    $('#callExchanges').text(response.exchanges + ' exchanges');
    $('#callFormat').text(response.format.toUpperCase() + (response.diarized ? ' (Diarized)' : ''));

    // Set download button
    $('#downloadBtn')
        .attr('href', response.audio_url)
        .attr('download', response.filename);

    // Show results section
    $('#resultsSection').removeClass('d-none');

    // Scroll to results
    $('html, body').animate({
        scrollTop: $('#resultsSection').offset().top - 100
    }, 500);
}

/**
 * Format duration in seconds to readable format
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return Math.round(seconds) + 's';
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);

    return minutes + 'm ' + remainingSeconds + 's';
}

/**
 * Load available voices from the API
 */
function loadVoices() {
    console.log('Loading voices...');

    $.ajax({
        url: '/api/voices',
        method: 'GET',
        success: function(response) {
            console.log('Voices loaded:', response);

            if (response.success && response.voices) {
                populateVoiceDropdowns(response.voices);
            } else {
                console.error('Failed to load voices');
                showVoiceLoadError();
            }
        },
        error: function(xhr) {
            console.error('Error loading voices:', xhr);
            showVoiceLoadError();
        }
    });
}

/**
 * Populate voice dropdown menus
 */
function populateVoiceDropdowns(voices) {
    const dispatcherSelect = $('#dispatcherVoice');
    const callerSelect = $('#callerVoice');

    // Clear existing options
    dispatcherSelect.empty();
    callerSelect.empty();

    // Add default option
    dispatcherSelect.append('<option value="">Select a voice...</option>');
    callerSelect.append('<option value="">Select a voice...</option>');

    // Add voice options
    voices.forEach(function(voice) {
        const optionText = voice.name + (voice.description ? ' - ' + voice.description.substring(0, 40) : '');
        const option = $('<option></option>')
            .attr('value', voice.voice_id)
            .text(optionText);

        dispatcherSelect.append(option.clone());
        callerSelect.append(option.clone());
    });

    // Set default selections if available
    if (voices.length > 0) {
        // Try to find professional/calm voices for dispatcher
        const dispatcherVoice = voices.find(v =>
            v.name.toLowerCase().includes('rachel') ||
            v.name.toLowerCase().includes('antoni') ||
            v.name.toLowerCase().includes('arnold')
        ) || voices[0];

        // Try to find emotional/varied voices for caller
        const callerVoice = voices.find(v =>
            v.name.toLowerCase().includes('bella') ||
            v.name.toLowerCase().includes('adam') ||
            v.name.toLowerCase().includes('elli')
        ) || voices[Math.min(1, voices.length - 1)];

        dispatcherSelect.val(dispatcherVoice.voice_id);
        callerSelect.val(callerVoice.voice_id);

        // Enable preview buttons
        $('#previewDispatcher').prop('disabled', false);
        $('#previewCaller').prop('disabled', false);
    }

    console.log('Voice dropdowns populated with ' + voices.length + ' voices');
}

/**
 * Show error when voices fail to load
 */
function showVoiceLoadError() {
    const errorOption = '<option value="">Error loading voices - please refresh</option>';
    $('#dispatcherVoice').html(errorOption);
    $('#callerVoice').html(errorOption);
}

/**
 * Preview a voice
 */
function previewVoice(voiceId, sampleText) {
    console.log('Previewing voice:', voiceId);

    // Disable preview buttons during generation
    $('#previewDispatcher, #previewCaller').prop('disabled', true);

    $.ajax({
        url: '/api/preview-voice',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            voice_id: voiceId,
            sample_text: sampleText
        }),
        xhrFields: {
            responseType: 'blob'
        },
        success: function(blob) {
            // Create audio element and play
            const audioUrl = URL.createObjectURL(blob);
            const audio = new Audio(audioUrl);

            audio.play().catch(function(error) {
                console.error('Error playing preview:', error);
                alert('Unable to play preview. Please try again.');
            });

            // Re-enable buttons after audio ends or 10 seconds
            audio.onended = function() {
                $('#previewDispatcher, #previewCaller').prop('disabled', false);
            };

            setTimeout(function() {
                $('#previewDispatcher, #previewCaller').prop('disabled', false);
            }, 10000);
        },
        error: function(xhr) {
            console.error('Error generating preview:', xhr);
            alert('Failed to generate voice preview. Please try again.');
            $('#previewDispatcher, #previewCaller').prop('disabled', false);
        }
    });
}
