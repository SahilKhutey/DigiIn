import { useState } from "react";
import { SafeAreaView, View, Text, TextInput, Pressable, StyleSheet, ScrollView } from "react-native";

const API = "http://localhost:8000/api/v1";

export default function Home(){
  const [email,setEmail] = useState("mobile@example.com");
  const [password,setPassword] = useState("password123");
  const [message,setMessage] = useState("Ready");

  async function start(){
    try{
      let r = await fetch(`${API}/auth/register`,{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email,password})
      });
      let d = await r.json();
      if(!r.ok){
        r = await fetch(`${API}/auth/login`,{
          method:"POST",headers:{"Content-Type":"application/json"},
          body:JSON.stringify({email,password})
        });
        d = await r.json();
      }
      setMessage(r.ok ? "Authenticated" : (d.detail ?? "Failed"));
    }catch(e:any){setMessage("API unavailable: check API URL/network");}
  }

  return <SafeAreaView style={s.page}><ScrollView>
    <Text style={s.brand}>DigiLocker X</Text>
    <Text style={s.title}>Your documents. Your verification. Your control.</Text>
    <Text style={s.copy}>Mobile foundation for credential, consent and verification journeys.</Text>
    <View style={s.card}>
      <Text>Email</Text>
      <TextInput style={s.input} value={email} onChangeText={setEmail}/>
      <Text>Password</Text>
      <TextInput style={s.input} secureTextEntry value={password} onChangeText={setPassword}/>
      <Pressable style={s.button} onPress={start}><Text style={s.buttonText}>Register / Login</Text></Pressable>
      <Text>{message}</Text>
    </View>
  </ScrollView></SafeAreaView>
}

const s=StyleSheet.create({
 page:{flex:1,backgroundColor:"#f7f8fa",padding:24},
 brand:{fontSize:22,fontWeight:"800",marginBottom:30},
 title:{fontSize:30,fontWeight:"800",lineHeight:36},
 copy:{fontSize:16,lineHeight:24,marginVertical:18},
 card:{backgroundColor:"#fff",padding:20,borderRadius:16,gap:10},
 input:{borderWidth:1,borderColor:"#ccd3db",padding:12,borderRadius:10},
 button:{backgroundColor:"#162d5a",padding:14,borderRadius:10,marginTop:10},
 buttonText:{color:"#fff",textAlign:"center",fontWeight:"700"}
});
