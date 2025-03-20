def caller():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:padding="20dp"
            android:gravity="center">

            <TextView
                android:id="@+id/tvPhoneNumber"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textSize="24sp"
                android:gravity="center"
                android:background="@android:color/darker_gray"
                android:padding="10dp"
                android:text=""/>

            <GridLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:columnCount="3"
                android:rowCount="4"
                android:alignmentMode="alignMargins"
                android:padding="10dp">

                <Button android:id="@+id/btn1" android:text="1" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn2" android:text="2" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn3" android:text="3" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn4" android:text="4" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn5" android:text="5" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn6" android:text="6" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn7" android:text="7" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn8" android:text="8" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btn9" android:text="9" android:onClick="onDigitClick"/>
                <Button android:id="@+id/btnDelete" android:text="DEL" android:onClick="onDeleteClick"/>
                <Button android:id="@+id/btn0" android:text="0" android:onClick="onDigitClick"/>
            </GridLayout>

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center"
                android:layout_marginTop="20dp">

                <Button
                    android:id="@+id/btnCall"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="CALL"
                    android:onClick="onCallClick"/>

                <Button
                    android:id="@+id/btnSave"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="SAVE"
                    android:layout_marginStart="20dp"
                    android:onClick="onSaveClick"/>
            </LinearLayout>

        </LinearLayout>
        """,
        """
        package com.example.program8dialer;

        import android.Manifest;
        import android.content.Intent;
        import android.net.Uri;
        import android.os.Bundle;
        import android.provider.ContactsContract;
        import android.view.View;
        import android.widget.Button;
        import android.widget.TextView;
        import android.widget.Toast;
        import androidx.appcompat.app.AppCompatActivity;
        import androidx.core.app.ActivityCompat;

        public class MainActivity extends AppCompatActivity {

            private TextView tvPhoneNumber;
            private static final int REQUEST_CALL_PERMISSION = 1;
            private static final int REQUEST_CONTACT_PERMISSION = 2;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                tvPhoneNumber = findViewById(R.id.tvPhoneNumber);

                // Request permissions for call and contacts
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CALL_PHONE}, REQUEST_CALL_PERMISSION);
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_CONTACTS}, REQUEST_CONTACT_PERMISSION);
            }

            public void onDigitClick(View view) {
                String digit = ((Button) view).getText().toString();
                tvPhoneNumber.append(digit);
            }

            public void onDeleteClick(View view) {
                String text = tvPhoneNumber.getText().toString();
                if (!text.isEmpty()) {
                    tvPhoneNumber.setText(text.substring(0, text.length() - 1));
                }
            }

            public void onCallClick(View view) {
                String phoneNumber = tvPhoneNumber.getText().toString();
                if (!phoneNumber.isEmpty()) {
                    Intent callIntent = new Intent(Intent.ACTION_CALL);
                    callIntent.setData(Uri.parse("tel:" + phoneNumber));
                    startActivity(callIntent);
                } else {
                    Toast.makeText(this, "Enter a phone number first!", Toast.LENGTH_SHORT).show();
                }
            }

            public void onSaveClick(View view) {
                String phoneNumber = tvPhoneNumber.getText().toString();
                if (!phoneNumber.isEmpty()) {
                    Intent saveIntent = new Intent(ContactsContract.Intents.Insert.ACTION);
                    saveIntent.setType(ContactsContract.RawContacts.CONTENT_TYPE);
                    saveIntent.putExtra(ContactsContract.Intents.Insert.PHONE, phoneNumber);
                    startActivity(saveIntent);
                    Toast.makeText(this, "Saving Contact...", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(this, "Enter a phone number first!", Toast.LENGTH_SHORT).show();
                }
            }
        }
        """,
        """AndroidManifest.xml""",
        """
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android"
            xmlns:tools="http://schemas.android.com/tools">

            <uses-feature
                android:name="android.hardware.telephony"
                android:required="false" />

            <uses-permission android:name="android.permission.CALL_PHONE"/>
            <uses-permission android:name="android.permission.WRITE_CONTACTS"/>
            <application
                android:allowBackup="true"
                android:dataExtractionRules="@xml/data_extraction_rules"
                android:fullBackupContent="@xml/backup_rules"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name"
                android:roundIcon="@mipmap/ic_launcher_round"
                android:supportsRtl="true"
                android:theme="@style/Theme.Program8Dialer"
                tools:targetApi="31">
                <activity
                    android:name=".MainActivity"
                    android:exported="true">
                    <intent-filter>
                        <action android:name="android.intent.action.MAIN" />

                        <category android:name="android.intent.category.LAUNCHER" />
                    </intent-filter>
                </activity>
            </application>

        </manifest>
        """
    ]