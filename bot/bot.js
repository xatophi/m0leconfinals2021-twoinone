const puppeteer = require('puppeteer')
const fs = require('fs')


const URL_TELEGRAM_CLIENT = process.env['URL_TELEGRAM_CLIENT'] 
const URL_TELEGRAM_LOGIN = URL_TELEGRAM_CLIENT + '/login'
const TOKEN = process.env['TOKEN'] || '2076003641:AAE2rI8UwX9ia00i1EPw6nrG3Dvi2Quouwc'
const LATITUDE = '45.06244678071925'
const LONGITUDE = '7.662078652110826'

const URL_NOTE = process.env['URL_NOTE']
const URL_NOTE_LOGIN = URL_NOTE + '/login'
const EMAIL_NOTE = process.env['EMAIL_NOTE']
const PASSWORD_NOTE = process.env['PASSWORD_NOTE']

const TIMEOUT = 1000*3

async function visit(url) {

    console.log('Running browser to visit "%s"', url);

	const browser = await puppeteer.launch({ 
        args: ['--no-sandbox'],
        executablePath: '/usr/bin/chromium'})

	// Authenticate
	let page = await browser.newPage()
    await page.setDefaultNavigationTimeout(TIMEOUT);

	await page.setRequestInterception(true)
	page.once('request', request => {

        if (request.url() == URL_TELEGRAM_LOGIN){
            let payload = 'bot_token=' + encodeURIComponent(TOKEN) + '&latitude=45.06244678071925&longitude=7.662078652110826'
            let data = {
                method: 'POST',
                postData: payload,
                headers: {
                    ...request.headers(),
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
            //console.log('____________')
            //console.log(request.url())
            request.continue(data)
        } else  {
            request.continue()
        }
	})
	
	try{
        //authenticate on telegram_bot_client
		await page.goto(URL_TELEGRAM_LOGIN)
        /*
        await page.waitForSelector('#inputToken')
        await page.focus('#inputToken')
        await page.keyboard.type(TOKEN, {delay: 10})
        await page.click('#submit')

        await page.waitForNavigation({waitUntil: 'networkidle2'});
        */
        page.removeAllListeners();
        await page.setRequestInterception(false)
        //console.log(await page.cookies())

        //authenticate on note
        await page.goto(URL_NOTE_LOGIN)
        await page.waitForSelector('#inputEmail')
        await page.focus('#inputEmail')
        await page.keyboard.type(EMAIL_NOTE, {delay: 10})
        await page.focus('#inputPassword')
        await page.keyboard.type(PASSWORD_NOTE, {delay: 10})
        await page.click('#submit')

        //console.log(await page.cookies())
		// Contacting URL after auth
        //console.log(url)
		await page.goto(url)

        // wait in the page
		await new Promise(resolve => setTimeout(resolve, TIMEOUT));
		await page.close()
		await browser.close()
	} catch (e){
		await browser.close()
		console.log(e)
        //throw(e)
  	}

}

module.exports = { visit }
