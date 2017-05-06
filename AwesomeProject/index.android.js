'use strict'

/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 * @flow
 */

import React, { Component } from 'react';
import { AppRegistry, Text } from 'react-native';

class HelloWorldApp extends Component {
  render() {
    postreceive();
    return (
      <Text>Hello world!</Text>
    );
  }
}

//

fetch('http://www.servu.ml/users/login', {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'Louis',
    password: 'Hello',
  })
})


async function postreceive() {
    try {
      let response = await fetch('http://www.servu.ml/users/login');
      console.log("receive !")
    } catch(error) {
      console.error(error);
    }
  }



AppRegistry.registerComponent('AwesomeProject', () => HelloWorldApp);