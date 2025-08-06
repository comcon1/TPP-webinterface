
const apiUrl = process.env.VUE_APP_API_URL;

function upload_func(obj, task) {
    const file = obj.$refs.fileInput.files[0]
    if (!file) {
    obj.error = 'Please select a PDB file.';
    return;
    }

    obj.loading = true;

    const formData = new FormData()
    formData.append('file', file)

    fetch(`${apiUrl}/queue_${task}/`, {
    method: 'POST',
    body: formData,
    })
    .then(async response => {
        if (!response.ok) {
        throw new Error('Server error: ' + (await response.text()))
        }
        var x = response.json();
        // console.log(JSON.stringify(x, null, 2));
        return x;
    })
    .then(data => {
        obj.taskIds.push(data.task_id);
    })
    .catch(err => {
        obj.error = 'Failed: ' + err.message;
    })
    .finally(() => {
        obj.show_processing = true;
    });
}

async function status_update(obj) {
    let statusLines = [];
    // we are now processing just one task at a time
    if (obj.taskIds.length == 1) {
    const id = obj.taskIds[0];
    try {
        const response = await fetch(`${apiUrl}/status/${id}`);
        const data = await response.json();
        statusLines.push(`Task ${id}: ${data.status}${data.result ? ' - result got.' : ''}`);
        if (data.status == 'SUCCESS') {
        clearInterval(obj.pollInterval);
        obj.result = data.result[0];
        obj.reslog = data.result[1];
        obj.loading = false;
        obj.taskIds.pop();
        }
    } catch (err) {
        statusLines.push(`Task ${id}: Error fetching status`);
    }
    }
    obj.processing = statusLines.join('\n');
}

export { upload_func, status_update, apiUrl };