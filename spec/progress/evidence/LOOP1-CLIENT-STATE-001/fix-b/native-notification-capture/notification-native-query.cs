using System;using System.Runtime.InteropServices;using System.Collections.Generic;
[ComImport,Guid("30cbe57d-d9d0-452a-ab13-7ac5ac4825ee"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]public interface OwnNativeUia {
 void M0();void M1();void GetRootElement(out OwnNativeElement root);
 void M3();void M4();void M5();void M6();void M7();void M8();void M9();void M10();void M11();void M12();void M13();void M14();void M15();void M16();void M17();void M18();void M19();void M20();
 void CreatePropertyConditionEx(int property,[MarshalAs(UnmanagedType.Struct)]object value,int flags,[MarshalAs(UnmanagedType.IUnknown)]out object condition);
}
[ComImport,Guid("d22108aa-8ac5-49a5-837b-37bbb3d7591e"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]public interface OwnNativeElement {
 void M0();void M1();void M2();void FindAll(int scope,[MarshalAs(UnmanagedType.IUnknown)]object condition,out OwnNativeArray found);
 void M4();void M5();void M6();void GetCurrentPropertyValue(int property,[MarshalAs(UnmanagedType.Struct)]out object value);
}
[ComImport,Guid("14314595-b4bc-4055-95f2-58f2e42c9855"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]public interface OwnNativeArray {void GetLength(out int length);void GetElement(int index,out OwnNativeElement element);}
public static class OwnSubstringQuery {
 public static object[] Find(){var u=(OwnNativeUia)Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("ff48dba4-60ef-4201-aa87-54103eef594e")));OwnNativeElement root;u.GetRootElement(out root);object condition;u.CreatePropertyConditionEx(30005,"Your workspace notifications are ready.",2,out condition);OwnNativeArray a;root.FindAll(4,condition,out a);int count;a.GetLength(out count);var results=new List<object>();for(int i=0;i<count;i++){OwnNativeElement e;a.GetElement(i,out e);var d=new Dictionary<string,object>();foreach(var p in new int[]{30005,30001,30002,30003,30012,30022}){object value;e.GetCurrentPropertyValue(p,out value);d[p.ToString()]=value;}results.Add(d);}return results.ToArray();}
}
