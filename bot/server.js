const express = require('express')
const bot = require('./bot')

const PORT = 9999


const app = express()

app.use(express.json());


app.post('/visit', async function (req, res) {
	res.set('Content-Type', 'text/html');

	const url = req.body.url;

	console.log('Visit requested for "%s"', url);
    
    if (url.startsWith('http')){
		try {
			bot.visit(url);
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