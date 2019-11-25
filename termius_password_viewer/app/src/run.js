const sjcl = require('rncryptor-js/sjcl')
const RNCryptor = require('rncryptor-js/src/rncryptor')
const $ = require('jquery')

const tableHeaders = {
    'label': '会话',
    'address': '地址',
    'port': '端口',
    'username': '用户名',
    'password': '密码'
}

const tableFieldsOrder = [
    'label',
    'address',
    'port',
    'username',
    'password'
]

var rnCryptor

function addRowHtml(fields) {
    resultTableBody = $('#result > tbody')[0]
    row = resultTableBody.insertRow()
    tableFieldsOrder.forEach(field => {
        cell = row.insertCell()
        cell.innerHTML = fields[field]
    })
}

function addRow(host, identity) {
    encryptedFields = []
    encryptedFields['label'] = host.label
    encryptedFields['address'] = host.address
    encryptedFields['username'] = identity.username
    encryptedFields['password'] = identity.password

    fields = []
    for (field in encryptedFields) {
        encrypted = encryptedFields[field]
        decrypted = encrypted ? rnCryptor.decrypt(encrypted) : ''
        fields[field] = decrypted
    }
    fields['port'] = host.ssh_config.port
    addRowHtml(fields)
}

function run() {
    hostsDbName = 'hosts'
    idDbName = 'ssh_identities'
    req = indexedDB.open(hostsDbName, 1)
    req.onsuccess = () => {
        transReq = req.result
            .transaction(hostsDbName)
            .objectStore(hostsDbName)
            .getAll()
        transReq.onsuccess = () => {
            result = transReq.result

            idDatabaseReq = indexedDB.open(idDbName, 1)
            idDatabaseReq.onsuccess = () => {

                result.forEach(host => {
                    let identityId = host.ssh_config.identity.id
                    let idValReq = idDatabaseReq.result
                        .transaction(idDbName)
                        .objectStore(idDbName)
                        .index('id')
                        .get(identityId)
                    idValReq.onsuccess = () => {
                        identity = idValReq.result
                        addRow(host, identity)
                    }
                })
            }
        }
    }
}

function initResultTable() {
    resultTable = $('#result')[0]
    headerRow = resultTable.createTHead().insertRow()
    tableFieldsOrder.forEach(field => {
        fieldHeader = tableHeaders[field]
        headerCell = document.createElement('th')
        cell = headerRow.appendChild(headerCell)
        cell.innerHTML = fieldHeader
    })
    resultTable.createTBody()
}

function getAccountSettings() {
    settingsDbName = 'settings'
    req = indexedDB.open(settingsDbName, 1)
    req.onsuccess = () => {
        let transReq
        try {
            transReq = req.result
                .transaction(settingsDbName)
                .objectStore(settingsDbName)
                .get("user")
        } catch (DOMException) {
            window.alert('未找到数据。')
            return
        }
        transReq.onsuccess = () => {
            result = transReq.result
            username = result.username_str
            if (username)
                $('#termiusAccount').text('“' + username + "”")
            hmacKey = result.secure_data.hmac_key
            encryptionKey = result.secure_data.encryption_key
            if (hmacKey && encryptionKey) {
                console.info('找到保存的密钥')
                rnCryptor = new RNCryptor({
                    hmacKey: hmacKey,
                    key: encryptionKey
                })
                run()
            }
        }
    }
}

$('document').ready(() => {
    initResultTable()
    getAccountSettings()
    $('form').submit(e => {
        e.preventDefault()
        password = $('#password').val()
        rnCryptor = new RNCryptor({ password: password })
        $('#result > tbody').text('')
        run()
    })
})

