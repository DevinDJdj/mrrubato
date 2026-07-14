

      document.addEventListener('DOMContentLoaded', function() {
        const loadEl = document.querySelector('#load');
        // // 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
        // // The Firebase SDK is initialized and available here!
        //
        const auth = firebase.auth();
        auth.onAuthStateChanged(user => { 
		  if (user) {
			// User is signed in, see docs for a list of available properties
			// https://firebase.google.com/docs/reference/js/firebase.User
            console.log(user);
				// ...
		  } else {
				// User is signed out
				// ...
		  }
		});
        // firebase.database().ref('/path/to/ref').on('value', snapshot => { });
        // firebase.firestore().doc('/foo/bar').get().then(() => { });
        // firebase.functions().httpsCallable('yourFunction')().then(() => { });
        // firebase.messaging().requestPermission().then(() => { });
        // firebase.storage().ref('/path/to/ref').getDownloadURL().then(() => { });
        // firebase.analytics(); // call to activate
        // firebase.analytics().logEvent('tutorial_completed');
        // firebase.performance(); // call to activate
        //
        // // 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

        try {
          let app = firebase.app();
          let features = [
            'auth', 
            'functions',
            'storage', 
			'database',
          ].filter(feature => typeof app[feature] === 'function');
          loadEl.textContent = `Firebase SDK loaded with ${features.join(', ')}`;

		  
        } catch (e) {
          console.error(e);
          loadEl.textContent = 'Error loading the Firebase SDK, check the console.';
        }
      });

function signIn() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const auth = firebase.auth();

    auth.signInWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Signed in successfully
            const user = userCredential.user;
            console.log('Signed in as:', user.email);
        })
        .catch((error) => {
            console.error('Sign in error:', error.message);
        });
}

function signUp() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const auth = firebase.auth();

    auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // Signed up successfully
            const user = userCredential.user;
            console.log('Signed up as:', user.email);
        })
        .catch((error) => {
            console.error('Sign up error:', error.message);
        });
}

