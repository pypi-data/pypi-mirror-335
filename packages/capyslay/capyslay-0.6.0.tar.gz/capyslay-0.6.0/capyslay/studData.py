def studData():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            android:id="@+id/main"
            android:layout_width="match_parent"
            android:orientation="vertical"
            android:layout_height="match_parent"
            android:padding="20dp">
            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Student Details"
                android:textSize="30dp"
                android:textAlignment="center"
                android:textStyle="bold"/>
            <EditText
                android:id="@+id/name"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Name"/>
            <EditText
                android:id="@+id/regno"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Regd.no"/>
            <EditText
                android:id="@+id/email"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Email"/>
            <EditText
                android:id="@+id/phno"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:hint="Mobile Number"/>
            <Button
                android:id="@+id/okbtn"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="OK"
                android:textSize="15dp"/>
            <TextView
                android:id="@+id/res"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="20dp"
                android:textSize="16dp"
                android:textAlignment="center"/>

        </LinearLayout>
        """,
        """
        package com.example.program2studet;

        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.EditText;
        import android.widget.TextView;

        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {
            Button okbtn;
            EditText name, mobnum, mail, regno;
            TextView res;

            @Override
            protected void onCreate(Bundle savedInstanceState) {

                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                okbtn = findViewById(R.id.okbtn);
                name = findViewById(R.id.name);
                mobnum = findViewById(R.id.phno);
                mail = findViewById(R.id.email);
                regno = findViewById(R.id.regno);
                res = findViewById(R.id.res);

                okbtn.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String sname = name.getText().toString();
                        String email = mail.getText().toString();
                        String sregno = regno.getText().toString();
                        String smobnum = mobnum.getText().toString();

                        String details = "Name : " + sname +
                                "\nRegd. No. : " + sregno +
                                "\nMail Id : " + email +
                                "\nMobile Number : " + smobnum;
                        res.setText(details);
                    }
                });

            }
        }
        """
    ]