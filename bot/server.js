const express = require('express')
const bot = require('./bot')
const {teams_bot_tokens, teams_last_visit} = require('./tokens')

const PORT = 9999
const RATE_LIMIT = 1000*30 // max one visit every 30s

const app = express()

app.use(express.json());


app.post('/visit', async function (req, res) {
	res.set('Content-Type', 'text/html');

	const url = req.body.url;
	const team_token = req.body.token;

	if (!url || !team_token){
		console.log('Visit requested with missing parameters');
		res.status(400);
		res.send('Missing parameters');
		return;
	}

	console.log('Visit requested for "%s" with teamtoken %s', url, team_token);
    
	const bot_token = teams_bot_tokens[team_token];

	if (!bot_token){
		console.log('Invalid token');
		res.status(400);
		res.send('Invalid token');
		return;
	}

	const last_visit = teams_last_visit[team_token];
	const ts = Date.now();

	if ((ts - last_visit) < RATE_LIMIT){
		console.log('Rate limit');
		res.status(400);
		res.send(`Please wait ${Math.round((RATE_LIMIT - (ts-last_visit))/1000)}s and retry`);
		return;
	}

	teams_last_visit[team_token] = ts;

    if (url.startsWith('http')){
		try {
			bot.visit(url, bot_token);
			res.send('ok');
			return;
		} catch (e) {
			console.log(e);
			res.status(500);
			res.send('failed');
			return;
		}
	}
	res.status(400);
    res.send('bad url');
})


app.listen(PORT, '0.0.0.0');
console.log('Listening on port %d ...',PORT);