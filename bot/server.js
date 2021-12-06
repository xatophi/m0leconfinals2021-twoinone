const express = require('express')
const bot = require('./bot')

const PORT = 9999
const RATE_LIMIT = 1000*30 // max one visit every 30s

const app = express()

app.use(express.json());


app.post('/visit', async function (req, res) {
	res.set('Content-Type', 'text/html');

	const url = req.body.url;
	const team_token = req.body.token;

	if (!url || !team_token || typeof team_token !== 'string' || typeof url !== 'string'){
		console.log('Visit requested with missing parameters');
		res.status(400);
		res.send('Missing parameters');
		return;
	}

	// token check removed

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