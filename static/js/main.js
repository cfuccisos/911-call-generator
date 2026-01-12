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

    // Load history on page load
    loadHistory();

    // Clear history button
    $('#clearHistory').on('click', function() {
        if (confirm('Are you sure you want to clear all prompt history?')) {
            localStorage.removeItem('promptHistory');
            loadHistory();
        }
    });

    // Protocol questions collapse toggle
    $('#protocolQuestionsSection').on('show.bs.collapse', function() {
        $('#toggleProtocolBtn').html('<i class="bi bi-dash-circle"></i> Hide Protocol Questions');
    });

    $('#protocolQuestionsSection').on('hide.bs.collapse', function() {
        $('#toggleProtocolBtn').html('<i class="bi bi-plus-circle"></i> Add Protocol Questions (Optional)');
    });

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
            protocol_questions: $('#protocolQuestions').val().trim(),
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

                // Save to history
                saveToHistory(formData);
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
    $('#protocolQuestions').prop('disabled', true);
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
    $('#protocolQuestions').prop('disabled', false);
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
    $('#callDurationDisplay').text(formatDuration(response.duration));
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

/**
 * Save generation settings to history
 */
function saveToHistory(formData) {
    try {
        // Get existing history from localStorage
        let history = JSON.parse(localStorage.getItem('promptHistory') || '[]');

        // Create history entry
        const entry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            prompt: formData.prompt,
            protocol_questions: formData.protocol_questions || '',
            call_duration: formData.call_duration,
            emotion_level: formData.emotion_level,
            audio_format: formData.audio_format,
            diarized: formData.diarized === 'true'
        };

        // Add to beginning of array
        history.unshift(entry);

        // Keep only last 10 entries
        history = history.slice(0, 10);

        // Save back to localStorage
        localStorage.setItem('promptHistory', JSON.stringify(history));

        // Reload history display
        loadHistory();
    } catch (e) {
        console.error('Error saving to history:', e);
    }
}

/**
 * Load and display history
 */
function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('promptHistory') || '[]');

        if (history.length === 0) {
            $('#historySection').addClass('d-none');
            return;
        }

        $('#historySection').removeClass('d-none');

        const historyList = $('#historyList');
        historyList.empty();

        history.forEach(function(entry) {
            const date = new Date(entry.timestamp);
            const timeStr = date.toLocaleString();
            const emotionLabel = entry.emotion_level.charAt(0).toUpperCase() + entry.emotion_level.slice(1);

            const historyItem = $(`
                <div class="card mb-2 history-item" data-id="${entry.id}" style="cursor: pointer;">
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="text-muted small">${timeStr}</div>
                                <div class="mt-1">${escapeHtml(entry.prompt)}</div>
                                <div class="mt-2">
                                    <span class="badge bg-secondary">${entry.call_duration}s</span>
                                    <span class="badge bg-info">${emotionLabel}</span>
                                    ${entry.protocol_questions ? '<span class="badge bg-warning text-dark">Protocol</span>' : ''}
                                    ${entry.diarized ? '<span class="badge bg-success">Diarized</span>' : ''}
                                </div>
                            </div>
                            <button class="btn btn-sm btn-outline-primary load-history-btn ms-2" data-id="${entry.id}">
                                <i class="bi bi-arrow-clockwise"></i> Load
                            </button>
                        </div>
                    </div>
                </div>
            `);

            historyList.append(historyItem);
        });

        // Add click handlers for load buttons
        $('.load-history-btn').on('click', function(e) {
            e.stopPropagation();
            const id = $(this).data('id');
            loadHistoryItem(id);
        });
    } catch (e) {
        console.error('Error loading history:', e);
    }
}

/**
 * Load a history item into the form
 */
function loadHistoryItem(id) {
    try {
        const history = JSON.parse(localStorage.getItem('promptHistory') || '[]');
        const entry = history.find(item => item.id === id);

        if (entry) {
            // Fill form with history data
            $('#prompt').val(entry.prompt);
            $('#protocolQuestions').val(entry.protocol_questions || '');
            $('#callDuration').val(entry.call_duration);
            $('#emotionLevel').val(entry.emotion_level);
            $('#audioFormat').val(entry.audio_format);
            $('#diarized').prop('checked', entry.diarized);

            // Update character count
            $('#charCount').text(entry.prompt.length);

            // If there are protocol questions, expand the section
            if (entry.protocol_questions) {
                const protocolSection = $('#protocolQuestionsSection');
                if (!protocolSection.hasClass('show')) {
                    protocolSection.collapse('show');
                }
            }

            // Scroll to form
            $('html, body').animate({
                scrollTop: $('#generateForm').offset().top - 100
            }, 500);
        }
    } catch (e) {
        console.error('Error loading history item:', e);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
