from flask import escape
import re


# check if the token format make sense
token_regex = re.compile(r"^\d+:[\w_-]{35}$")
def is_token_safe(token):
    if(token_regex.fullmatch(token)):
        return True
    return False


# convert the telegram message following the formatting defined at https://core.telegram.org/type/MessageEntity
def parse_telegram_style(msg):
    if 'text' not in msg:
        return ''
    elif 'entities' not in msg:
        # no entities, just text
        return str(escape(msg['text']))
    else:
        # parse each entity
        entities = msg['entities']
        text = msg['text']
        res = ''
        i = 0
        
        for e in entities:
            off = e['offset']
            length = e['length']
            t = e['type']

            res += str(escape(text[i:off]))
            
            entity_text = str(escape(text[off:off+length]))
            i = off+length

            if t == 'code':
                res += f'<code>{entity_text}</code>'
            elif t == 'bold':
                res += f'<b>{entity_text}</b>'
            elif t == 'text_link':
                if 'url' not in e:
                    res += f'<a href={entity_text}>{entity_text}</a>'
                else:
                    res += f'<a href={e["url"]}>{entity_text}</a>'
            elif t == 'pre':
                if entity_text[0] == '\n' or '\n' not in entity_text:
                    res += f'<pre class=prettyprint>{entity_text}</pre>'
                else:
                    i = entity_text.find('\n')
                    language = entity_text[:i]
                    entity_text = entity_text[i+1:]
                    res += f'<pre class=prettyprint><code class=language-{language}>{entity_text}</code></pre>'
            elif t == 'underline':
                res += f'<u>{entity_text}</u>'
            elif t == 'italic':
                res += f'<i>{entity_text}</i>'
            elif t == 'strikethrough':
                res += f'<s>{entity_text}</s>'
            else:
                res += entity_text

        return res