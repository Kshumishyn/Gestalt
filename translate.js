const translate = require('translate');

let text = 'Fuck you and the horse you rode in on.';

translate(text, { to: 'ja', engine: 'yandex', key: 'trnsl.1.1.20190430T034509Z.5878c41cdd8a259f.d9c7b3bc52dbe22e4e349c5bb11b7f6b8379d23f' }).then(function(result) {
    console.log(result); // "initResolve"
	return "normalReturn";
});
