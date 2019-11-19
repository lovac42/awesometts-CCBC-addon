# Awesomo and AwesomeTTS

## AWESOM-O (Application)
Awesomo is a wrapper that launches AwesomeTTS without the need for Anki. This allows the program to be used independent of Anki allowing more creative applications such as a screen reader or clipboard text reader.

Supermemo users may find this useful as there isn't a need to download 150mb of useless files just to use AwesomeTTS.

#### Running Awesom-o from source:
Awesom-o uses the same toolkit as Anki 2.0 and the same dependencies (Qt4, QtWebkit). This is because Webkit has a small footprint resulting in a compiled size of around 30MB on Windows, whereas WebEngine results in over 160MB.

To run from source, just type:
```
Python3 runawesomo.py
```

Note however, that the older dependencies will become harder to find and install and most likely must be compiled from source. As my intention was to run this on windows for personal use, independent of Anki, this is not much of an issue for me.


## AwesomeTTS (Library)
AwesomeTTS makes it easy for language-learners and other students to add
speech to their personal [Anki](https://apps.ankiweb.net) card decks.

Once loaded into the Anki `addons` directory, the AwesomeTTS add-on code
enables both on-demand playback and recording functionality.


### Changes for cloze:
Cloze patterns during review are now spoken as ```[What]``` instead of ```...``` (blank). This is to prevent conflicts with text that includes actual ellipses. You can search and replace this if you prefer a different text to be spoken.  
<img src="https://github.com/lovac42/awesometts-CCBC-addon/blob/unified/screenshots/cloze_regex.png?raw=true" />  


### Changes from current official v1.12.0:
Fixed Naver issue (used eescueta's version)  
Fixed Neospeech (has demo tag on mp3)  
Fixed Oxford (Now Lexico.com and only British en-GB is available)  
Added Oxford Learner's Dictionary  
Added Google Cloud TTS service by Nickolay (kelciour)  
Added Cambridge Dictionary by m-rtin  
Added Forvo service by Dador  
Added TextAloud (Polly) service  
Added Merriam-Webster (I stole it from Nickolay https://ankiweb.net/shared/info/1878363231)  
Added Azure by lucwastiaux: I can't confirm this because I don't have an API key to test it.


### Needs to fix:
abair  
baidu  
duden  
fluency.nl  
wikitionary  
yandex  

WatsonTTS: demo service has ended?  


Added Bing Translator, without a key, the connection maybe unreliable.  
<img src="https://github.com/lovac42/awesometts-CCBC-addon/blob/unified/screenshots/bing.png?raw=true" />  



## Hooks:

```
runHook('AwesomeTTS.speak', "hello world") # say hello world with OS default voice (SAPI)

runHook('AwesomeTTS.silence', 5) # adds 5 secs of silence

runHook('AwesomeTTS.config', callback) # get the config settings
```
