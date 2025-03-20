def signin():
    return [
        """
        main_activity.xml
        """,
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:padding="20dp">

            <EditText
                android:id="@+id/etUsername"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Username" />

            <EditText
                android:id="@+id/etPassword"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Password"
                android:inputType="textPassword" />

            <Button
                android:id="@+id/btnSignup"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="SIGN UP" />
        </LinearLayout>
        """,
        """
        package com.example.program4signup;

        import android.content.Intent;
        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import android.widget.Toast;
        import java.util.regex.Pattern;

        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {
            EditText etUsername, etPassword;
            Button btnSignup;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                etUsername = findViewById(R.id.etUsername);
                etPassword = findViewById(R.id.etPassword);
                btnSignup = findViewById(R.id.btnSignup);

                btnSignup.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String username = etUsername.getText().toString().trim();
                        String password = etPassword.getText().toString().trim();

                        if (validatePassword(password)) {
                            Intent intent = new Intent(MainActivity.this, activity_login.class);
                            intent.putExtra("USERNAME", username);
                            intent.putExtra("PASSWORD", password);
                            startActivity(intent);
                        } else {
                            Toast.makeText(MainActivity.this, "Password must contain:\n" +
                                    "- At least 8 characters\n" +
                                    "- At least one uppercase letter\n" +
                                    "- At least one lowercase letter\n" +
                                    "- At least one number\n" +
                                    "- At least one special character", Toast.LENGTH_LONG).show();
                        }

                    }
                });
            }

            private boolean validatePassword(String password) {
                if (password.length() < 8) return false;
                if (!Pattern.compile("[A-Z]").matcher(password).find()) return false;
                if (!Pattern.compile("[a-z]").matcher(password).find()) return false;
                if (!Pattern.compile("[0-9]").matcher(password).find()) return false;
                if (!Pattern.compile("[^a-zA-Z0-9]").matcher(password).find()) return false;

                return true;
            }
        }
        """,
        """login.xml""",
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:padding="20dp">

            <EditText
                android:id="@+id/etLoginUsername"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Username" />

            <EditText
                android:id="@+id/etLoginPassword"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Password"
                android:inputType="textPassword" />

            <Button
                android:id="@+id/btnLogin"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="SIGN IN" />
        </LinearLayout>
        """,
        """login.java""",
        """
        package com.example.program4signup;

        import android.content.Intent;
        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import android.widget.Toast;
        import androidx.appcompat.app.AppCompatActivity;

        public class activity_login extends AppCompatActivity {
            EditText etLoginUsername, etLoginPassword;
            Button btnLogin;
            String savedUsername, savedPassword;
            int loginAttempts = 0;

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_login);

                etLoginUsername = findViewById(R.id.etLoginUsername);
                etLoginPassword = findViewById(R.id.etLoginPassword);
                btnLogin = findViewById(R.id.btnLogin);

                Intent intent = getIntent();
                savedUsername = intent.getStringExtra("USERNAME");
                savedPassword = intent.getStringExtra("PASSWORD");

                btnLogin.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String username = etLoginUsername.getText().toString().trim();
                        String password = etLoginPassword.getText().toString().trim();

                        if (username.equals(savedUsername) && password.equals(savedPassword)) {
                            Toast.makeText(activity_login.this, "Successful Login", Toast.LENGTH_SHORT).show();
                        } else {
                            loginAttempts++;
                            if (loginAttempts >= 2) {
                                Toast.makeText(activity_login.this, "Failed Login Attempts", Toast.LENGTH_SHORT).show();
                                btnLogin.setEnabled(false);
                            } else {
                                Toast.makeText(activity_login.this, "Login Failed", Toast.LENGTH_SHORT).show();
                            }
                        }
                    }
                });
            }
        }
        """,
        """AndroidManifest.xml""",
        """
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android"
            xmlns:tools="http://schemas.android.com/tools">

            <application
                android:allowBackup="true"
                android:dataExtractionRules="@xml/data_extraction_rules"
                android:fullBackupContent="@xml/backup_rules"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name"
                android:roundIcon="@mipmap/ic_launcher_round"
                android:supportsRtl="true"
                android:theme="@style/Theme.Program4signup"
                tools:targetApi="31">
                <activity
                    android:name=".activity_login"
                    android:exported="false" />
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