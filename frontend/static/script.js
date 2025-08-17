class HRAgentApp {
    constructor() {
        this.selectedCandidates = [];
        this.loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        this.initEventListeners();
    }
    
    initEventListeners() {
        // File input change handler
        document.getElementById('resumes').addEventListener('change', (e) => {
            this.displaySelectedFiles(e.target.files);
        });
        
        // Process button
        document.getElementById('processBtn').addEventListener('click', () => {
            this.processResumes();
        });
        
        // Select all checkbox
        document.getElementById('selectAll').addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });
        
        // Select top candidates button
        document.getElementById('selectTopBtn').addEventListener('click', () => {
            this.selectTopCandidates();
        });
        
        // Schedule interviews button
        document.getElementById('scheduleBtn').addEventListener('click', () => {
            this.scheduleInterviews();
        });
        
        // Send emails button
        document.getElementById('sendEmailsBtn').addEventListener('click', () => {
            this.sendConfirmationEmails();
        });
    }
    
    displaySelectedFiles(files) {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';
        
        Array.from(files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileName = document.createElement('span');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            const fileSize = document.createElement('span');
            fileSize.className = 'file-size';
            fileSize.textContent = this.formatFileSize(file.size);
            
            fileItem.appendChild(fileName);
            fileItem.appendChild(fileSize);
            fileList.appendChild(fileItem);
        });
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async processResumes() {
        // Validate form
        const form = document.getElementById('jobForm');
        const resumeInput = document.getElementById('resumes');
        
        if (!form.checkValidity() || resumeInput.files.length === 0) {
            alert('Please fill all required fields and select PDF files.');
            return;
        }
        
        // Show loading
        this.showLoading('Processing Resumes', 'Analyzing resumes and ranking candidates...');
        
        try {
            // Prepare form data
            const formData = new FormData();
            
            // Add job description data
            const formInputs = form.querySelectorAll('input, textarea');
            formInputs.forEach(input => {
                formData.append(input.name, input.value);
            });
            
            // Add resume files
            Array.from(resumeInput.files).forEach(file => {
                formData.append('resumes', file);
            });
            
            // Send request
            const response = await fetch('/api/process_job', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result);
                this.showAlert('success', `Successfully processed ${result.candidates.length} candidates!`);
            } else {
                this.showAlert('danger', result.error || 'Processing failed');
            }
            
        } catch (error) {
            console.error('Error processing resumes:', error);
            this.showAlert('danger', 'An error occurred while processing resumes');
        } finally {
            this.hideLoading();
        }
    }
    
    displayResults(result) {
        const resultsSection = document.getElementById('results-section');
        const candidatesTable = document.getElementById('candidates-table');
        const totalCandidates = document.getElementById('total-candidates');
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Update total count
        totalCandidates.textContent = result.candidates.length;
        
        // Clear and populate table
        candidatesTable.innerHTML = '';
        
        result.candidates.forEach((candidate, index) => {
            const row = this.createCandidateRow(candidate, index + 1);
            candidatesTable.appendChild(row);
        });
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    createCandidateRow(candidate, rank) {
        const row = document.createElement('tr');
        row.className = 'candidate-row';
        
        // Get score colors
        const overallScoreClass = this.getScoreClass(candidate.overall_score);
        const skillScoreClass = this.getScoreClass(candidate.skill_match_score);
        const expScoreClass = this.getScoreClass(candidate.experience_score);
        
        row.innerHTML = `
            <td><input type="checkbox" class="candidate-checkbox" value="${candidate.name}"></td>
            <td><strong>${rank}</strong></td>
            <td><strong>${candidate.name}</strong></td>
            <td><small>${candidate.email}</small></td>
            <td><span class="badge bg-secondary">${candidate.experience}</span></td>
            <td><span class="badge ${skillScoreClass} score-badge">${candidate.skill_match_score}%</span></td>
            <td><span class="badge ${expScoreClass} score-badge">${candidate.experience_score}%</span></td>
            <td><span class="badge ${overallScoreClass} score-badge">${candidate.overall_score}%</span></td>
            <td><span class="candidate-summary" title="${candidate.summary}">${candidate.summary}</span></td>
        `;
        
        // Add checkbox event listener
        const checkbox = row.querySelector('.candidate-checkbox');
        checkbox.addEventListener('change', () => {
            this.updateSelectedCandidates();
        });
        
        return row;
    }
    
    getScoreClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        return 'bg-danger';
    }
    
    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.candidate-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
        });
        this.updateSelectedCandidates();
    }
    
    selectTopCandidates() {
        // Uncheck all first
        document.querySelectorAll('.candidate-checkbox').forEach(cb => cb.checked = false);
        
        // Select top 5
        const topCheckboxes = document.querySelectorAll('.candidate-checkbox');
        for (let i = 0; i < Math.min(5, topCheckboxes.length); i++) {
            topCheckboxes[i].checked = true;
        }
        
        this.updateSelectedCandidates();
    }
    
    updateSelectedCandidates() {
        const checkboxes = document.querySelectorAll('.candidate-checkbox:checked');
        this.selectedCandidates = Array.from(checkboxes).map(cb => cb.value);
        
        // Enable/disable buttons
        document.getElementById('scheduleBtn').disabled = this.selectedCandidates.length === 0;
        
        // Update select all checkbox
        const selectAllCheckbox = document.getElementById('selectAll');
        const allCheckboxes = document.querySelectorAll('.candidate-checkbox');
        selectAllCheckbox.checked = this.selectedCandidates.length === allCheckboxes.length;
        selectAllCheckbox.indeterminate = this.selectedCandidates.length > 0 && 
            this.selectedCandidates.length < allCheckboxes.length;
    }
    
    async scheduleInterviews() {
        if (this.selectedCandidates.length === 0) {
            this.showAlert('warning', 'Please select candidates to schedule interviews.');
            return;
        }

        const startDate = document.getElementById('scheduleDate').value;
        if (!startDate) {
            this.showAlert('warning', 'Please choose a start date.');
            return;
        }
        
        this.showLoading('Scheduling Interviews', 'Creating calendar events and scheduling interviews...');
        
        try {
            // First, send selected candidates
            await fetch('/api/select_candidates', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ selected_candidates: this.selectedCandidates })
            });
            
            // Then schedule interviews using chosen start date
            const response = await fetch('/api/schedule_interviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    selected_candidates: this.selectedCandidates,
                    start_date: startDate
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayInterviewSchedule(result.interview_summary);
                this.showAlert('success', result.message);
                document.getElementById('sendEmailsBtn').disabled = false;
            } else {
                this.showAlert('danger', result.error || 'Scheduling failed');
            }
        } catch (error) {
            console.error('Error scheduling interviews:', error);
            this.showAlert('danger', 'An error occurred while scheduling interviews');
        } finally {
            this.hideLoading();
        }
    }
    
    displayInterviewSchedule(schedule) {
        const scheduleSection = document.getElementById('schedule-section');
        const scheduleContent = document.getElementById('schedule-content');
        
        scheduleSection.style.display = 'block';
        
        let html = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle"></i> Successfully scheduled ${schedule.total_scheduled} interviews</h6>
            </div>
        `;
        
        schedule.schedule_details.forEach(interview => {
            const link = interview.meet_link && interview.meet_link !== 'Not available' ? interview.meet_link : '#';
            const disabled = link === '#' ? 'disabled' : '';
            html += `
                <div class="interview-item">
                    <div class="row align-items-center">
                        <div class="col-md-4">
                            <div class="candidate-name">${interview.candidate_name}</div>
                            <div class="text-muted">${interview.email}</div>
                        </div>
                        <div class="col-md-4">
                            <div class="interview-time">
                                <i class="fas fa-calendar"></i> ${interview.datetime}
                            </div>
                        </div>
                        <div class="col-md-4 text-md-end mt-2 mt-md-0">
                            <a href="${link}" target="_blank" class="btn btn-outline-primary btn-sm" ${disabled}>
                                <i class="fas fa-video"></i> Join Meeting
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        
        scheduleContent.innerHTML = html;
        scheduleSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    async sendConfirmationEmails() {
        this.showLoading('Sending Emails', 'Sending confirmation emails to selected candidates...');
        
        try {
            const response = await fetch('/api/send_confirmations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('success', result.message);
            } else {
                this.showAlert('danger', result.error || 'Failed to send emails');
            }
        } catch (error) {
            console.error('Error sending emails:', error);
            this.showAlert('danger', 'An error occurred while sending emails');
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading(title, message) {
        document.getElementById('loadingMessage').textContent = title;
        document.getElementById('loadingDetail').textContent = message;
        this.loadingModal.show();
    }
    
    hideLoading() {
        this.loadingModal.hide();
    }
    
    showAlert(type, message) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container-fluid').prepend(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.hrAgentApp = new HRAgentApp();
});
