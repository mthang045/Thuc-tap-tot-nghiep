/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * Generated with the TypeScript template
 * https://github.com/react-native-community/react-native-template-typescript
 *
 * @format
 */

import React, { useEffect, useMemo, useState } from 'react';
import {
  SafeAreaView,
  Text,
  StatusBar,
  TouchableOpacity,
  View,
  ScrollView,
  StyleSheet,
  Linking,
  DeviceEventEmitter,
  NativeEventEmitter,
  Alert
} from 'react-native';
import { COLOR } from 'react-native-material-ui'
import VnpayMerchant, { VnpayMerchantModule } from './react-native-vnpay-merchant'
const eventEmitter = new NativeEventEmitter(VnpayMerchantModule);

type SdkItem = {
  id: number;
  framework: string;
  codeUrl: string;
  guideText: string;
}

const SDK_ITEMS: SdkItem[] = [
  { id: 1, framework: 'IOS Native', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
  { id: 2, framework: 'IOS Native Swift', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
  { id: 3, framework: 'Android Native', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
  { id: 4, framework: 'React Native', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
  { id: 5, framework: 'Flutter', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
  { id: 6, framework: 'Kotlin Multiplatform', codeUrl: 'https://sandbox.vnpayment.vn/apis/docs/chuyen-doi-thuat-toan/changeTypeHash.html', guideText: 'Tài liệu tích hợp' },
]


const App = () => {
  const [text, setText] = useState('Open SDK')

  const openLink = async (url: string) => {
    const canOpen = await Linking.canOpenURL(url)
    if (!canOpen) {
      Alert.alert('Lỗi', 'Không thể mở đường dẫn này')
      return
    }
    await Linking.openURL(url)
  }

  const openVnpayDemo = (paymentUrl: string, title: string) => {
    eventEmitter.addListener('PaymentBack', (e) => {
      if (e) {
        console.log('PaymentBack resultCode =', e.resultCode)
        eventEmitter.removeAllListeners('PaymentBack')
      }
    })

    VnpayMerchant.show({
      isSandbox: true,
      scheme: 'sampleapp',
      title,
      titleColor: '#333333',
      beginColor: '#ffffff',
      endColor: '#ffffff',
      tmn_code: 'GOGREEN1',
      paymentUrl,
    })
    setText('SDK opened')
  }

  const headers = useMemo(() => ['STT', 'Hỗ trợ ngôn ngữ LT/Framework', 'Download', 'Hướng dẫn'], [])

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.title}>Tích hợp SDK Mobile Cổng thanh toán VNPAY</Text>

          <View style={styles.table}>
            <View style={[styles.row, styles.headerRow]}>
              <Text style={[styles.cell, styles.headerCell, styles.sttCol]}>{headers[0]}</Text>
              <Text style={[styles.cell, styles.headerCell, styles.frameworkCol]}>{headers[1]}</Text>
              <Text style={[styles.cell, styles.headerCell, styles.linkCol]}>{headers[2]}</Text>
              <Text style={[styles.cell, styles.headerCell, styles.linkCol]}>{headers[3]}</Text>
            </View>

            {SDK_ITEMS.map((item, index) => (
              <View key={item.id} style={[styles.row, index % 2 === 0 ? styles.rowEven : styles.rowOdd]}>
                <Text style={[styles.cell, styles.sttCol]}>{item.id}</Text>
                <Text style={[styles.cell, styles.frameworkCol]}>{item.framework}</Text>
                <TouchableOpacity style={[styles.cell, styles.linkCol]} onPress={() => openLink(item.codeUrl)}>
                  <Text style={styles.linkText}>Tải về code demo</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.cell, styles.linkCol]} onPress={() => openLink(item.codeUrl)}>
                  <Text style={styles.linkText}>{item.guideText}</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>

          <View style={styles.actions}>
            <TouchableOpacity
              style={styles.primaryButton}
              onPress={() => openVnpayDemo('https://sandbox.vnpayment.vn/testsdk', 'Thanh toán VNPAY Demo')}
            >
              <Text style={styles.buttonText}>Mở SDK Demo</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => openVnpayDemo('https://sandbox.vnpayment.vn/tryitnow/Home/CreateOrder', 'Thanh toán VNPAY Order')}
            >
              <Text style={styles.buttonText}>Mở SDK Với URL Đơn Hàng</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.statusText}>Trạng thái: {text}</Text>
        </ScrollView>
      </SafeAreaView>
    </>
  );
};


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fb',
  },
  content: {
    padding: 16,
    paddingBottom: 36,
  },
  title: {
    fontSize: 30,
    fontWeight: '700',
    color: '#18233a',
    marginBottom: 14,
  },
  table: {
    borderWidth: 1,
    borderColor: '#d8dee8',
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#ffffff',
  },
  row: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#edf1f7',
    minHeight: 52,
    alignItems: 'center',
  },
  headerRow: {
    backgroundColor: '#eef2f8',
  },
  rowEven: {
    backgroundColor: '#ffffff',
  },
  rowOdd: {
    backgroundColor: '#f9fbff',
  },
  cell: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    color: '#12213d',
  },
  headerCell: {
    fontWeight: '700',
    color: '#0e1d39',
  },
  sttCol: {
    width: 46,
  },
  frameworkCol: {
    flex: 1,
  },
  linkCol: {
    width: 108,
    justifyContent: 'center',
  },
  linkText: {
    color: '#1063f3',
    textDecorationLine: 'underline',
  },
  actions: {
    marginTop: 18,
    gap: 12,
  },
  primaryButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: COLOR.blue600,
    borderRadius: 8,
    alignItems: 'center',
  },
  secondaryButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1f7a8c',
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: COLOR.white,
    fontSize: 15,
    fontWeight: '600',
  },
  statusText: {
    marginTop: 14,
    fontSize: 14,
    color: '#283b5b',
  },
})



export default App;
