package im.platform.client.ui.components
import androidx.compose.runtime.*
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.*

import im.platform.client.ui.*
import im.platform.client.ui.i18n.*
@Composable fun Login(state:WorkspaceState,login:(String,String,String)->Unit,register:(String,String,String)->Unit,restore:(String)->Unit) {
    val t=useText()

    var registering by remember{mutableStateOf(false)};var username by remember{mutableStateOf("")};var password by remember{mutableStateOf("")};var confirmation by remember{mutableStateOf("")}
    LaunchedEffect(state.registered){if(state.registered){registering=false;password="";confirmation=""}}
    Column(Modifier.fillMaxWidth().imePadding().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(14.dp)){
        Text(t("auth.stayCloseMobile"),fontSize=(state.appearance.fontSize+10).sp,lineHeight=((state.appearance.fontSize+10)*1.25f).sp,fontWeight=FontWeight.Bold)
        Panel(Modifier.fillMaxWidth(),state.appearance){
            Text(if(registering)t("auth.createTitle")else t("auth.openTitle"),style=MaterialTheme.typography.titleLarge)
            if(state.registered&&!registering)Text(t("auth.created"))
            OutlinedTextField(value=username,onValueChange={username=it},label={Text(t("auth.username"))},singleLine=true,modifier=Modifier.fillMaxWidth())
            OutlinedTextField(value=password,onValueChange={password=it},label={Text(t("auth.password"))},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth())
            if(registering){OutlinedTextField(value=confirmation,onValueChange={confirmation=it},label={Text(t("auth.confirmPassword"))},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth());Text(t("auth.passwordHint"),style=MaterialTheme.typography.bodyMedium)}
            Button(onClick={if(registering)register(username,password,confirmation)else{login(state.endpoint,username,password);password=""}},enabled=!state.busy&&username.isNotEmpty()&&password.isNotEmpty()&&(!registering||confirmation.isNotEmpty()),modifier=Modifier.fillMaxWidth()){Text(if(state.busy)t("auth.wait")else if(registering)t("auth.create")else t("auth.signIn"))}
            TextButton(onClick={registering=!registering;password="";confirmation=""},enabled=!state.busy,modifier=Modifier.fillMaxWidth()){Text(if(registering)t("auth.existing")else t("auth.new"))}
            if(!registering)TextButton(onClick={restore(state.endpoint)},enabled=!state.busy,modifier=Modifier.fillMaxWidth()){Text(t("auth.resume"))}
        }
    }
}
