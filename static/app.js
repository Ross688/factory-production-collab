// 工厂项目管理系统 - 自定义 JavaScript

(function() {
    'use strict';

    // 自动关闭 flash 消息
    document.addEventListener('DOMContentLoaded', function() {
        // 5秒后自动关闭提示
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            setTimeout(function() {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });

        // 确认操作弹窗
        document.querySelectorAll('[data-confirm]').forEach(function(el) {
            el.addEventListener('click', function(e) {
                var msg = this.dataset.confirm || '确定要执行此操作吗？';
                if (!confirm(msg)) {
                    e.preventDefault();
                }
            });
        });

        // Shop-floor workspace interactions
        var quantityValue = document.querySelector('[data-quantity-value]');
        document.querySelectorAll('[data-quantity-change]').forEach(function(button) {
            button.addEventListener('click', function() {
                if (!quantityValue) return;
                var next = Math.max(1, parseInt(quantityValue.textContent || '1', 10) + parseInt(this.dataset.quantityChange, 10));
                quantityValue.textContent = next;
            });
        });

        document.querySelectorAll('.workspace-shell [data-action="pause"]').forEach(function(button) {
            button.addEventListener('click', function() {
                button.classList.toggle('is-paused');
                button.innerHTML = button.classList.contains('is-paused')
                    ? '<i class="bi bi-play-fill"></i> 继续'
                    : '<i class="bi bi-pause-fill"></i> 暂停';
                var notice = document.createElement('div');
                notice.className = 'workspace-toast';
                notice.textContent = button.classList.contains('is-paused') ? '任务已暂停' : '任务已继续';
                document.body.appendChild(notice);
                setTimeout(function() { notice.remove(); }, 1800);
            });
        });

        document.querySelectorAll('.workspace-shell .step-status-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                var stepId = this.dataset.stepId;
                var status = this.dataset.status;
                fetch('/api/step/' + stepId + '/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: status})
                }).then(function(response) {
                    if (response.status === 401) { window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname); return null; }
                    return response.json();
                }).then(function(result) {
                    if (result && result.success) window.location.reload();
                });
            });
        });

        var sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('workspace-collapsed');
        });
    });

})();
