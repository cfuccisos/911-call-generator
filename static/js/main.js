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

    // Load pre-loaded scripts on page load
    loadScripts();

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

    // Call type change handler
    $('#callType').on('change', function() {
        updateUIForCallType($(this).val());
    });

    // Initialize UI based on default call type
    updateUIForCallType($('#callType').val());

    // Background noise type change handler
    $('#backgroundNoiseType').on('change', function() {
        const noiseType = $(this).val();
        if (noiseType === 'none') {
            $('#noiseLevelSection').hide();
        } else {
            $('#noiseLevelSection').show();
        }
    });

    // Script source toggle handler
    $('input[name="scriptSource"]').on('change', function() {
        const source = $(this).val();
        if (source === 'preloaded') {
            // Show pre-loaded script selector
            $('#preloadedScriptSection').show();

            // Hide all scenario configuration sections
            $('#scenarioConfigSection').hide(); // Call type & duration
            $('#customPromptSection').hide(); // Custom prompt textarea
            $('#protocolQuestionsToggle').hide(); // Protocol questions
            $('#emotionLevelSection').hide(); // Emotion level
            $('#erraticLevelSection').hide(); // Erratic behavior

            // Mark prompt as not required
            $('#prompt').prop('required', false);

            // Keep language, voice, and audio settings visible
        } else {
            // Hide pre-loaded script selector
            $('#preloadedScriptSection').hide();

            // Show scenario configuration sections
            $('#scenarioConfigSection').show(); // Call type & duration
            $('#customPromptSection').show(); // Custom prompt textarea
            $('#protocolQuestionsToggle').show(); // Protocol questions

            // Mark prompt as required
            $('#prompt').prop('required', true);

            // Update UI based on current call type (emotion/erratic visibility)
            updateUIForCallType($('#callType').val());
        }
    });

    // Initialize noise level visibility
    if ($('#backgroundNoiseType').val() !== 'none') {
        $('#noiseLevelSection').show();
    }

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

    $('#previewNurse').on('click', function() {
        const voiceId = $('#nurseVoice').val();
        if (voiceId) {
            previewVoice(voiceId, 'I understand. Can you tell me more about your symptoms?');
        }
    });

    // Enable preview buttons when voice is selected
    $('#dispatcherVoice').on('change', function() {
        $('#previewDispatcher').prop('disabled', !$(this).val());
    });

    $('#callerVoice').on('change', function() {
        $('#previewCaller').prop('disabled', !$(this).val());
    });

    $('#nurseVoice').on('change', function() {
        $('#previewNurse').prop('disabled', !$(this).val());
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
        const usePreloadedCheck = $('input[name="scriptSource"]:checked').val() === 'preloaded';
        const initialMessage = usePreloadedCheck ? 'Loading script...' : 'Generating dialogue...';
        showLoading(initialMessage);

        // Disable form
        disableForm();

        // Get form data
        const usePreloaded = $('input[name="scriptSource"]:checked').val() === 'preloaded';
        const callType = $('#callType').val();

        const formData = {
            use_preloaded: usePreloaded ? 'true' : 'false',
            script_filename: usePreloaded ? $('#scriptSelector').val() : '',
            prompt: $('#prompt').val().trim(),
            call_type: callType,
            language: $('#language').val(),
            dispatcher_protocol_questions: $('#dispatcherProtocolQuestions').val().trim(),
            nurse_protocol_questions: $('#nurseProtocolQuestions').val().trim(),
            call_duration: $('#callDuration').val(),
            emotion_level: $('#emotionLevel').val(),
            erratic_level: $('#erraticLevel').val(),
            audio_format: $('#audioFormat').val(),
            audio_quality: $('#audioQuality').val(),
            background_noise_type: $('#backgroundNoiseType').val(),
            background_noise_level: $('#backgroundNoiseLevel').val(),
            diarized: $('#diarized').is(':checked') ? 'true' : 'false',
            dispatcher_voice_id: $('#dispatcherVoice').val(),
            caller_voice_id: $('#callerVoice').val(),
            nurse_voice_id: $('#nurseVoice').val() || ''
        };

        // Add translator-specific language parameters
        if (callType === 'with_translator') {
            formData.dispatcher_language = $('#dispatcherLanguage').val();
            formData.caller_language = $('#callerLanguage').val();
        }

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
    $('#callType').prop('disabled', true);
    $('#prompt').prop('disabled', true);
    $('#dispatcherProtocolQuestions').prop('disabled', true);
    $('#nurseProtocolQuestions').prop('disabled', true);
    $('#callDuration').prop('disabled', true);
    $('#emotionLevel').prop('disabled', true);
    $('#erraticLevel').prop('disabled', true);
    $('#dispatcherVoice').prop('disabled', true);
    $('#callerVoice').prop('disabled', true);
    $('#nurseVoice').prop('disabled', true);
    $('#audioFormat').prop('disabled', true);
    $('#audioQuality').prop('disabled', true);
    $('#backgroundNoiseType').prop('disabled', true);
    $('#backgroundNoiseLevel').prop('disabled', true);
    $('#diarized').prop('disabled', true);
    $('#previewDispatcher').prop('disabled', true);
    $('#previewCaller').prop('disabled', true);
    $('#previewNurse').prop('disabled', true);
}

/**
 * Enable form inputs
 */
function enableForm() {
    $('#generateBtn').prop('disabled', false).html(
        '<i class="bi bi-play-circle"></i> Generate Call'
    );
    $('#callType').prop('disabled', false);
    $('#prompt').prop('disabled', false);
    $('#dispatcherProtocolQuestions').prop('disabled', false);
    $('#nurseProtocolQuestions').prop('disabled', false);
    $('#callDuration').prop('disabled', false);
    $('#emotionLevel').prop('disabled', false);
    $('#erraticLevel').prop('disabled', false);
    $('#dispatcherVoice').prop('disabled', false);
    $('#callerVoice').prop('disabled', false);
    $('#nurseVoice').prop('disabled', false);
    $('#audioFormat').prop('disabled', false);
    $('#audioQuality').prop('disabled', false);
    $('#backgroundNoiseType').prop('disabled', false);
    $('#backgroundNoiseLevel').prop('disabled', false);
    $('#diarized').prop('disabled', false);
    $('#previewDispatcher').prop('disabled', $('#dispatcherVoice').val() === '');
    $('#previewCaller').prop('disabled', $('#callerVoice').val() === '');
    $('#previewNurse').prop('disabled', $('#nurseVoice').val() === '');
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
    const nurseSelect = $('#nurseVoice');

    // Clear existing options
    dispatcherSelect.empty();
    callerSelect.empty();
    nurseSelect.empty();

    // Add default option
    dispatcherSelect.append('<option value="">Select a voice...</option>');
    callerSelect.append('<option value="">Select a voice...</option>');
    nurseSelect.append('<option value="">Select a voice...</option>');

    // Add voice options
    voices.forEach(function(voice) {
        // Extract name and first part of description for compact display
        const nameParts = voice.name.split(' - ');
        const voiceName = nameParts[0];

        // Get first 2 descriptors if available (e.g., "Laid-Back, Casual" from "Laid-Back, Casual, Resonant")
        let shortDesc = '';
        if (nameParts.length > 1 && nameParts[1].trim()) {
            const descriptors = nameParts[1].split(',').map(d => d.trim());
            shortDesc = ' - ' + descriptors.slice(0, 2).join(', ');
        } else if (voice.description) {
            // If no dash descriptor but has a description field, use first 30 chars
            shortDesc = ' - ' + voice.description.substring(0, 30);
            if (voice.description.length > 30) shortDesc += '...';
        }

        const displayText = voiceName + shortDesc;

        // Build comprehensive tooltip with all available info
        let tooltipText = voice.name;
        if (voice.description && voice.description !== voice.name) {
            tooltipText += ': ' + voice.description;
        }

        const option = $('<option></option>')
            .attr('value', voice.voice_id)
            .text(displayText)
            .attr('title', tooltipText);

        dispatcherSelect.append(option.clone());
        callerSelect.append(option.clone());
        nurseSelect.append(option.clone());
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

        // Try to find calm/professional voices for nurse
        const nurseVoice = voices.find(v =>
            v.name.toLowerCase().includes('sarah') ||
            v.name.toLowerCase().includes('grace') ||
            v.name.toLowerCase().includes('domi')
        ) || voices[Math.min(2, voices.length - 1)];

        dispatcherSelect.val(dispatcherVoice.voice_id);
        callerSelect.val(callerVoice.voice_id);
        nurseSelect.val(nurseVoice.voice_id);

        // Enable preview buttons
        $('#previewDispatcher').prop('disabled', false);
        $('#previewCaller').prop('disabled', false);
        $('#previewNurse').prop('disabled', false);
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
    $('#nurseVoice').html(errorOption);
}

/**
 * Load pre-loaded scripts from server
 */
function loadScripts() {
    console.log('Loading pre-loaded scripts...');

    $.ajax({
        url: '/api/scripts',
        method: 'GET',
        success: function(scripts) {
            console.log('Scripts loaded:', scripts);

            const scriptSelector = $('#scriptSelector');
            scriptSelector.empty();

            if (scripts && scripts.length > 0) {
                scriptSelector.append('<option value="">Select a script...</option>');

                scripts.forEach(function(script) {
                    const option = $('<option></option>')
                        .attr('value', script.filename)
                        .text(script.title)
                        .attr('title', script.description);
                    scriptSelector.append(option);
                });

                console.log('Script dropdown populated with ' + scripts.length + ' scripts');
            } else {
                scriptSelector.append('<option value="">No scripts available</option>');
            }
        },
        error: function(xhr) {
            console.error('Error loading scripts:', xhr);
            $('#scriptSelector').html('<option value="">Error loading scripts</option>');
        }
    });
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
            call_type: formData.call_type,
            dispatcher_protocol_questions: formData.dispatcher_protocol_questions || '',
            nurse_protocol_questions: formData.nurse_protocol_questions || '',
            call_duration: formData.call_duration,
            emotion_level: formData.emotion_level,
            erratic_level: formData.erratic_level,
            audio_format: formData.audio_format,
            audio_quality: formData.audio_quality,
            background_noise_type: formData.background_noise_type,
            background_noise_level: formData.background_noise_level,
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
            const callTypeLabel = entry.call_type === 'transfer' ? 'Transfer' : 'Emergency';
            const callTypeBadge = entry.call_type === 'transfer' ? 'bg-primary' : 'bg-secondary';

            const historyItem = $(`
                <div class="card mb-2 history-item" data-id="${entry.id}">
                    <div class="card-body p-3">
                        <div class="row align-items-center">
                            <div class="col">
                                <div class="text-muted small mb-1">${timeStr}</div>
                                <div class="mb-2">${escapeHtml(entry.prompt)}</div>
                                <div>
                                    <span class="badge ${callTypeBadge}">${callTypeLabel}</span>
                                    <span class="badge bg-secondary">${entry.call_duration}s</span>
                                    ${entry.call_type !== 'transfer' ? `<span class="badge bg-info">${emotionLabel}</span>` : ''}
                                    ${(entry.dispatcher_protocol_questions || entry.nurse_protocol_questions || entry.protocol_questions) ? '<span class="badge bg-warning text-dark">Protocol</span>' : ''}
                                    ${entry.diarized ? '<span class="badge bg-success">Diarized</span>' : ''}
                                </div>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-sm btn-outline-primary load-history-btn" data-id="${entry.id}">
                                    <i class="bi bi-arrow-clockwise"></i> Load
                                </button>
                            </div>
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
            $('#callType').val(entry.call_type || 'emergency');
            updateUIForCallType(entry.call_type || 'emergency');

            $('#prompt').val(entry.prompt);

            // Handle both old and new protocol question formats
            $('#dispatcherProtocolQuestions').val(entry.dispatcher_protocol_questions || entry.protocol_questions || '');
            $('#nurseProtocolQuestions').val(entry.nurse_protocol_questions || '');

            $('#callDuration').val(entry.call_duration);
            $('#emotionLevel').val(entry.emotion_level);
            $('#erraticLevel').val(entry.erratic_level || 'none');
            $('#audioFormat').val(entry.audio_format);
            $('#audioQuality').val(entry.audio_quality || 'high');

            // Handle both old and new background noise formats
            $('#backgroundNoiseType').val(entry.background_noise_type || entry.background_noise || 'none');
            $('#backgroundNoiseLevel').val(entry.background_noise_level || 'moderate');

            // Show/hide noise level section based on type
            if ($('#backgroundNoiseType').val() !== 'none') {
                $('#noiseLevelSection').show();
            } else {
                $('#noiseLevelSection').hide();
            }

            $('#diarized').prop('checked', entry.diarized);

            // Update character count
            $('#charCount').text(entry.prompt.length);

            // If there are protocol questions, expand the section
            if (entry.dispatcher_protocol_questions || entry.nurse_protocol_questions || entry.protocol_questions) {
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

/**
 * Update UI labels and visibility based on call type
 */
function updateUIForCallType(callType) {
    if (callType === 'with_translator') {
        // Emergency call with translator (3-way: dispatcher -> translator -> caller)
        $('#promptLabel').text('Emergency Scenario Description');
        $('#prompt').attr('placeholder', 'Describe the emergency scenario... (e.g., "Car accident with Spanish-speaking caller needing assistance")');

        $('#voice1Label').text('Dispatcher Voice');
        $('#voice1Help').text('911 dispatcher (speaks dispatcher language)');

        $('#voice2Label').text('Caller Voice');
        $('#voice2Help').text('Emergency caller (speaks caller language)');

        // Protocol questions
        $('#dispatcherProtocolLabel').text('Protocol Questions');
        $('#dispatcherProtocolHelp').text('Specific questions the dispatcher must ask');
        $('#nurseProtocolSection').hide();

        // Show nurse voice section for translator
        $('#nurseVoiceSection').show();
        $('#nurseVoice').prop('required', true);
        $('#voice3Label').text('Translator Voice');
        $('#voice3Help').text('Bilingual translator facilitating communication');

        // Show emotion level and erratic level
        $('#emotionLevelSection').show();
        $('#erraticLevelSection').show();

        // Show multi-language sections
        $('#singleLanguageSection').hide();
        $('#multiLanguageSection').show();

    } else if (callType === 'transfer') {
        // Dispatcher-to-dispatcher transfer
        $('#promptLabel').text('Transfer Scenario Description');
        $('#prompt').attr('placeholder', 'Describe the incident being transferred... (e.g., "Active shooter situation at downtown mall, transferring to SWAT commander")');

        $('#voice1Label').text('Transferring Dispatcher Voice');
        $('#voice1Help').text('Initial dispatcher transferring the call');

        $('#voice2Label').text('Receiving Dispatcher Voice');
        $('#voice2Help').text('Dispatcher or supervisor receiving the transfer');

        // Protocol questions
        $('#dispatcherProtocolLabel').text('Protocol Questions');
        $('#dispatcherProtocolHelp').text('Specific questions the transferring dispatcher must ask');
        $('#nurseProtocolSection').hide();

        // Hide emotion level and erratic level for dispatcher transfers
        $('#emotionLevelSection').hide();
        $('#erraticLevelSection').hide();

        // Hide nurse voice section
        $('#nurseVoiceSection').hide();
        $('#nurseVoice').prop('required', false);

        // Show single language, hide multi-language
        $('#singleLanguageSection').show();
        $('#multiLanguageSection').hide();

    } else if (callType === 'warm_transfer') {
        // Warm transfer to nurse (3-way: dispatcher -> nurse -> caller)
        $('#promptLabel').text('Warm Transfer Scenario Description');
        $('#prompt').attr('placeholder', 'Describe the medical situation... (e.g., "Caller experiencing chest pain and shortness of breath, transferring to nurse triage")');

        $('#voice1Label').text('Dispatcher Voice');
        $('#voice1Help').text('911 dispatcher initiating the transfer');

        $('#voice2Label').text('Caller Voice');
        $('#voice2Help').text('Person calling with medical concern');

        // Protocol questions - show both sections
        $('#dispatcherProtocolLabel').text('Dispatcher Protocol Questions');
        $('#dispatcherProtocolHelp').text('Questions the dispatcher should ask before transferring');
        $('#nurseProtocolSection').show();

        // Show nurse voice section
        $('#nurseVoiceSection').show();
        $('#nurseVoice').prop('required', true);
        $('#voice3Label').text('Nurse Voice');
        $('#voice3Help').text('Triage nurse providing medical assessment');

        // Show emotion level and erratic level for caller
        $('#emotionLevelSection').show();
        $('#erraticLevelSection').show();

        // Show single language, hide multi-language
        $('#singleLanguageSection').show();
        $('#multiLanguageSection').hide();

    } else {
        // Emergency call (dispatcher to caller)
        $('#promptLabel').text('Emergency Scenario Description');
        $('#prompt').attr('placeholder', 'Describe the emergency scenario... (e.g., "Car accident on Highway 101 with multiple injuries")');

        $('#voice1Label').text('Dispatcher Voice');
        $('#voice1Help').text('Professional, calm voice for the 911 dispatcher');

        $('#voice2Label').text('Caller Voice');
        $('#voice2Help').text('Emotional, varied voice for the emergency caller');

        // Protocol questions
        $('#dispatcherProtocolLabel').text('Protocol Questions');
        $('#dispatcherProtocolHelp').text('Specific questions the dispatcher must ask during the call');
        $('#nurseProtocolSection').hide();

        // Show emotion level and erratic level for emergency calls
        $('#emotionLevelSection').show();
        $('#erraticLevelSection').show();

        // Hide nurse voice section
        $('#nurseVoiceSection').hide();
        $('#nurseVoice').prop('required', false);

        // Show single language, hide multi-language
        $('#singleLanguageSection').show();
        $('#multiLanguageSection').hide();
    }
}
