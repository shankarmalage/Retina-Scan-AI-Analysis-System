// Firebase imports
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.2/firebase-app.js";
import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    updateProfile 
} from "https://www.gstatic.com/firebasejs/10.7.2/firebase-auth.js";

// Firebase config
const firebaseConfig = {
    apiKey: "AIzaSyC1DrJXOVd3qH8_KiMNaQtT3Bf6nU09xWs",
    authDomain: "drdetection-3f9c7.firebaseapp.com",
    projectId: "drdetection-3f9c7",
    storageBucket: "drdetection-3f9c7.firebasestorage.app",
    messagingSenderId: "419516848286",
    appId: "1:419516848286:web:cce492e5a74307d69a038f",
    measurementId: "G-KK0QSFFTFG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
