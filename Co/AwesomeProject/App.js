import React, { Component } from 'react';
import {
    AppRegistry,
    StyleSheet,
    Text,
    View,
    ListView,
    Platform,
    TouchableOpacity
} from 'react-native';
import { ReactNativeAudioStreaming, Player } from 'react-native-audio-streaming';
import SocketIOClient from 'socket.io-client';

export default class App extends Component {
    constructor() {
        super();
        this.ds = new ListView.DataSource({rowHasChanged: (r1, r2) => r1 !== r2});
        this.urls = [
            {
                name: 'Shoutcast stream',
                url: 'http://192.168.43.19:5000/stream.mp3'
            }
        ];

        this.state = {
            dataSource: this.ds.cloneWithRows(this.urls),
            selectedSource: this.urls[0].url
        };

        this.socket = SocketIOClient('http://192.168.43.19:5000');
        this.socket.on('order', this.exec_order);
    }


    exec_order(data){
        console.log(data);
        if (data.value.length >= 10){
            let url = `http://192.168.43.19:5000/music/${data.value}.mp3`
            ReactNativeAudioStreaming.play(url , {showIniOSMediaCenter: true, showInAndroidNotifications: true});
            ReactNativeAudioStreaming.pause();
        }

        if ( data.value == "1"){
            ReactNativeAudioStreaming.resume();
        }

        if( data.value == "2")
            ReactNativeAudioStreaming.pause();
    }

    render() {
        return (
            <View style={styles.container}>
                <ListView
                    dataSource={this.state.dataSource}
                    renderRow={(rowData) =>
                        <TouchableOpacity onPress={() => {
                            this.setState({selectedSource: rowData.url, dataSource: this.ds.cloneWithRows(this.urls)});
                            ReactNativeAudioStreaming.play(rowData.url, {});
                        }}>
                            <View style={StyleSheet.flatten([
                                styles.row,
                                {backgroundColor: rowData.url == this.state.selectedSource ? '#3fb5ff' : 'white'}
                            ])}>
                                <Text style={styles.icon}>▸</Text>
                                <View style={styles.column}>
                                    <Text style={styles.name}>{rowData.name}</Text>
                                    <Text style={styles.url}>{rowData.url}</Text>
                                </View>
                            </View>
                        </TouchableOpacity>
                    }
                />

                <Player url={this.state.selectedSource} />
            </View>
        );
    }
}



const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F5FCFF',
        paddingTop: Platform.OS === 'ios' ? 30 : 0
    },
    row: {
        flex: 1,
        flexDirection: 'row',
        padding: 5,
        borderBottomColor: 'grey',
        borderBottomWidth: 1
    },
    column: {
        flexDirection: 'column'
    },
    icon: {
        fontSize: 26,
        width: 30,
        textAlign: 'center'
    },
    name: {
        color: '#000'
    },
    url: {
        color: '#CCC'
    }
});
